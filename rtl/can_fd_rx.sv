`timescale 1ns/1ps

// CAN / CAN FD receiver, ISO 11898-1:2015, one wire bit per clock.
//
// CLASSIC=0 (CAN FD):
//   DYN      - dynamically stuffed region (SOF..data). CRC is fed with the
//              STUFFED stream (stuff bits included), per ISO CAN FD.
//   CRC_LEAD - leading fixed stuff bit of the CRC field.
//   CRC_SEQ  - stuff count + CRC, fixed stuff bit before each 4-bit group.
//
// CLASSIC=1 (Classic CAN 2.0):
//   DYN      - dynamically stuffed region (SOF..data). CRC-15 is fed with the
//              DESTUFFED stream: stuff bits are checked but NOT fed to the CRC.
//   CRC_READ - the 15-bit CRC field, itself dynamically stuffed. Stuff bits are
//              discarded here too. No stuff count, no fixed stuff bits.
//
//   TAIL     - CRC delimiter, ACK slot, ACK delimiter, EOF x7 (both modes).
module can_fd_rx #(
    parameter bit EXTENDED = 0,
    parameter bit CLASSIC  = 0
)(
    input  wire         clk, rst_n,
    input  wire         rx_bit,
    output wire         rx_ack,
    output reg  [28:0]  rx_id,
    output reg  [3:0]   rx_dlc,
    output reg  [511:0] rx_data,
    output reg          rx_done,
    output reg          rx_valid,
    output reg          rx_crc_err,
    output reg          rx_stuff_err
);
    localparam IDLE=4'd0, DYN=4'd1, CRC_LEAD=4'd2, CRC_SEQ=4'd3,
               TAIL=4'd4, DONE=4'd5, CRC_READ=4'd6;
    reg [3:0] state;

    reg [10:0] raw_idx;
    reg [10:0] raw_total_r;
    reg [2:0]  run_len;
    reg        run_bit;
    reg        expect_stuff;
    reg [7:0]  dyn;
    reg [3:0]  dlc_shift;
    reg        brs_seen;
    reg        form_err;

    reg [16:0] crc17;
    reg [20:0] crc21;
    reg [14:0] crc15;
    reg [20:0] crc_rx;
    reg [14:0] crc15_rx;
    reg [4:0]  seq_idx;
    reg [2:0]  grp_cnt;
    reg [3:0]  tail_idx;
    reg [3:0]  crc15_idx;

    wire is_crc21 = (rx_dlc >= 4'd11);
    wire [4:0] cw = is_crc21 ? 5'd21 : 5'd17;
    wire [20:0] crc_mask = is_crc21 ? 21'h1FFFFF : 21'h01FFFF;
    wire [20:0] crc_calc = is_crc21 ? crc21 : {4'd0, crc17};

    wire [10:0] header_len = CLASSIC ? (EXTENDED ? 11'd39 : 11'd19)
                                     : (EXTENDED ? 11'd41 : 11'd22);
    wire [10:0] dlc_base = header_len - 11'd4;
    wire [1:0]  dlc_off  = raw_idx[1:0] - dlc_base[1:0];

    wire [10:0] dpos       = raw_idx - header_len;
    wire [8:0]  data_idx   = 9'd511 - dpos[8:0];
    wire [4:0]  ida_idx    = 5'd29 - raw_idx[4:0];
    wire [4:0]  idb_idx    = 5'd31 - raw_idx[4:0];
    wire [4:0]  idbase_idx = 5'd11 - raw_idx[4:0];

    function [16:0] crc17_step(input [16:0] c, input b);
        reg m; reg [16:0] sh;
        begin
            m = c[16]; sh = {c[15:0], 1'b0};
            crc17_step = (m ^ b) ? (sh ^ 17'h1685B) : sh;
        end
    endfunction

    function [20:0] crc21_step(input [20:0] c, input b);
        reg m; reg [20:0] sh;
        begin
            m = c[20]; sh = {c[19:0], 1'b0};
            crc21_step = (m ^ b) ? (sh ^ 21'h102899) : sh;
        end
    endfunction

    function [14:0] crc15_step(input [14:0] c, input b);
        reg m; reg [14:0] sh;
        begin
            m = c[14]; sh = {c[13:0], 1'b0};
            crc15_step = (m ^ b) ? (sh ^ 15'h4599) : sh;
        end
    endfunction

    function [6:0] dlc_bytes(input [3:0] d);
        begin
            case (d)
                4'd0,4'd1,4'd2,4'd3,4'd4,4'd5,4'd6,4'd7,4'd8: dlc_bytes = {3'd0, d};
                4'd9:  dlc_bytes = 7'd12;
                4'd10: dlc_bytes = 7'd16;
                4'd11: dlc_bytes = 7'd20;
                4'd12: dlc_bytes = 7'd24;
                4'd13: dlc_bytes = 7'd32;
                4'd14: dlc_bytes = 7'd48;
                4'd15: dlc_bytes = 7'd64;
                default: dlc_bytes = 7'd0;
            endcase
        end
    endfunction

    // Classic CAN clamps the payload to 8 bytes for DLC > 8.
    function [6:0] payload_bytes(input [3:0] d);
        reg [6:0] n;
        begin
            n = dlc_bytes(d);
            if (CLASSIC && n > 7'd8) n = 7'd8;
            payload_bytes = n;
        end
    endfunction

    assign rx_ack = (state == TAIL && tail_idx == 4'd1) ? 1'b0 : 1'b1;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state <= IDLE;
            rx_done <= 1'b0; rx_valid <= 1'b0;
            rx_crc_err <= 1'b0; rx_stuff_err <= 1'b0; form_err <= 1'b0;
            raw_idx <= 11'd0; raw_total_r <= header_len;
            run_len <= 3'd0; run_bit <= 1'b1; expect_stuff <= 1'b0;
            dyn <= 8'd0; dlc_shift <= 4'd0; brs_seen <= 1'b0;
            crc17 <= 17'd0; crc21 <= 21'd0; crc15 <= 15'd0;
            crc_rx <= 21'd0; crc15_rx <= 15'd0;
            seq_idx <= 5'd0; grp_cnt <= 3'd0; tail_idx <= 4'd0; crc15_idx <= 4'd0;
            rx_id <= 29'd0; rx_dlc <= 4'd0; rx_data <= 512'd0;
        end else begin
            rx_done  <= 1'b0;
            rx_valid <= 1'b0;

            case (state)
                IDLE: begin
                    if (rx_bit == 1'b0) begin
                        crc17 <= crc17_step(17'h10000, 1'b0);
                        crc21 <= crc21_step(21'h100000, 1'b0);
                        crc15 <= crc15_step(15'h0000, 1'b0);
                        raw_idx      <= 11'd1;
                        raw_total_r  <= header_len;
                        run_len      <= 3'd1;
                        run_bit      <= 1'b0;
                        expect_stuff <= 1'b0;
                        dyn          <= 8'd0;
                        dlc_shift    <= 4'd0;
                        brs_seen     <= 1'b0;
                        crc_rx       <= 21'd0;
                        crc15_rx     <= 15'd0;
                        seq_idx      <= 5'd0;
                        grp_cnt      <= 3'd0;
                        tail_idx     <= 4'd0;
                        crc15_idx    <= 4'd0;
                        rx_crc_err   <= 1'b0;
                        rx_stuff_err <= 1'b0;
                        form_err     <= 1'b0;
                        rx_id        <= 29'd0;
                        rx_dlc       <= 4'd0;
                        rx_data      <= 512'd0;
                        state        <= DYN;
                    end
                end

                DYN: begin
                    if (expect_stuff) begin
                        if (rx_bit != ~run_bit) rx_stuff_err <= 1'b1;
                        // CAN FD: stuff bits ARE part of the CRC input.
                        // Classic: CRC is over the DESTUFFED stream -> skip.
                        if (!CLASSIC) begin
                            crc17 <= crc17_step(crc17, rx_bit);
                            crc21 <= crc21_step(crc21, rx_bit);
                        end
                        dyn          <= dyn + 8'd1;
                        run_bit      <= rx_bit;
                        run_len      <= 3'd1;
                        expect_stuff <= 1'b0;
                    end else begin
                        if (CLASSIC) begin
                            crc15 <= crc15_step(crc15, rx_bit);
                        end else begin
                            crc17 <= crc17_step(crc17, rx_bit);
                            crc21 <= crc21_step(crc21, rx_bit);
                        end

                        if (EXTENDED) begin
                            if (raw_idx >= 11'd1 && raw_idx <= 11'd11)
                                rx_id[ida_idx] <= rx_bit;
                            else if (raw_idx >= 11'd14 && raw_idx <= 11'd31)
                                rx_id[idb_idx] <= rx_bit;
                        end else begin
                            if (raw_idx >= 11'd1 && raw_idx <= 11'd11)
                                rx_id[idbase_idx] <= rx_bit;
                        end

                        if (!CLASSIC && !EXTENDED && raw_idx == 11'd16)
                            brs_seen <= rx_bit;
                        else if (!CLASSIC && EXTENDED && raw_idx == 11'd35)
                            brs_seen <= rx_bit;

                        if (raw_idx >= dlc_base && raw_idx <= header_len - 11'd1) begin
                            case (dlc_off)
                                2'd0: rx_dlc[3] <= rx_bit;
                                2'd1: rx_dlc[2] <= rx_bit;
                                2'd2: rx_dlc[1] <= rx_bit;
                                2'd3: rx_dlc[0] <= rx_bit;
                            endcase
                            dlc_shift <= {dlc_shift[2:0], rx_bit};
                        end
                        else if (raw_idx >= header_len)
                            rx_data[data_idx] <= rx_bit;

                        if (rx_bit == run_bit) begin
                            run_len <= run_len + 3'd1;
                            if (run_len == 3'd4) expect_stuff <= 1'b1;
                        end else begin
                            run_bit <= rx_bit;
                            run_len <= 3'd1;
                        end

                        raw_idx <= raw_idx + 11'd1;

                        if (raw_idx == header_len - 11'd1) begin
                            raw_total_r <= header_len +
                                ({4'd0, payload_bytes({dlc_shift[2:0], rx_bit})} << 3);
                            if (payload_bytes({dlc_shift[2:0], rx_bit}) == 7'd0) begin
                                if (CLASSIC) begin
                                    crc15_idx <= 4'd0;
                                    state <= CRC_READ;
                                end else begin
                                    state <= CRC_LEAD;
                                end
                            end
                        end else if (raw_idx >= header_len &&
                                     (raw_idx + 11'd1) == raw_total_r) begin
                            if (CLASSIC) begin
                                crc15_idx <= 4'd0;
                                state <= CRC_READ;
                            end else begin
                                state <= CRC_LEAD;
                            end
                        end
                    end
                end

                CRC_LEAD: begin
                    seq_idx <= 5'd0;
                    grp_cnt <= 3'd0;
                    state   <= CRC_SEQ;
                end

                CRC_SEQ: begin
                    if (grp_cnt == 3'd4) begin
                        grp_cnt <= 3'd0;
                    end else begin
                        if (seq_idx < 5'd4) begin
                            crc17 <= crc17_step(crc17, rx_bit);
                            crc21 <= crc21_step(crc21, rx_bit);
                        end else begin
                            crc_rx <= {crc_rx[19:0], rx_bit};
                        end
                        seq_idx <= seq_idx + 5'd1;
                        grp_cnt <= grp_cnt + 3'd1;
                        if ((seq_idx + 5'd1) == (5'd4 + cw)) begin
                            tail_idx <= 4'd0;
                            state    <= TAIL;
                        end
                    end
                end

                // Classic CAN: the 15-bit CRC field is itself dynamically
                // stuffed. Discard stuff bits, do not feed them anywhere.
                CRC_READ: begin
                    if (expect_stuff) begin
                        if (rx_bit != ~run_bit) rx_stuff_err <= 1'b1;
                        run_bit      <= rx_bit;
                        run_len      <= 3'd1;
                        expect_stuff <= 1'b0;
                    end else begin
                        crc15_rx  <= {crc15_rx[13:0], rx_bit};
                        crc15_idx <= crc15_idx + 4'd1;

                        if (rx_bit == run_bit) begin
                            run_len <= run_len + 3'd1;
                            if (run_len == 3'd4) expect_stuff <= 1'b1;
                        end else begin
                            run_bit <= rx_bit;
                            run_len <= 3'd1;
                        end

                        if (crc15_idx == 4'd14) begin
                            tail_idx <= 4'd0;
                            state    <= TAIL;
                        end
                    end
                end

                TAIL: begin
                    if (tail_idx == 4'd0) begin
                        if (rx_bit != 1'b1) form_err <= 1'b1;
                        if (CLASSIC) begin
                            if (crc15_rx != crc15) rx_crc_err <= 1'b1;
                        end else begin
                            if ((crc_rx & crc_mask) != (crc_calc & crc_mask))
                                rx_crc_err <= 1'b1;
                        end
                    end else if (tail_idx >= 4'd2) begin
                        if (rx_bit != 1'b1) form_err <= 1'b1;
                    end
                    tail_idx <= tail_idx + 4'd1;
                    if (tail_idx == 4'd9) state <= DONE;
                end

                DONE: begin
                    rx_done  <= 1'b1;
                    rx_valid <= ~(rx_crc_err | rx_stuff_err | form_err);
                    state    <= IDLE;
                end

                default: state <= IDLE;
            endcase
        end
    end
endmodule
