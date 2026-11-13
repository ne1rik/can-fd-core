`timescale 1ns/1ps

// CAN FD receiver, ISO 11898-1:2015, FBFF (11-bit ID), one wire bit per clock.
//
// Structure:
//   DYN      - dynamically stuffed region (SOF..data). Stuff bits are discarded.
//   CRC_LEAD - leading fixed stuff bit of the CRC field (always present).
//   CRC_SEQ  - stuff count + CRC bits, with a fixed stuff bit before each
//              subsequent 4-bit group.
//   TAIL     - CRC delimiter, ACK slot, ACK delimiter, EOF x7.
//
// CRC-17 and CRC-21 are computed in parallel from SOF onward, because the
// payload length (and therefore the CRC width and init value) is only known
// after the DLC field has been received.
module can_fd_rx (
    input  wire         clk, rst_n,
    input  wire         rx_bit,
    output wire         rx_ack,
    output reg  [10:0]  rx_id,
    output reg  [3:0]   rx_dlc,
    output reg  [511:0] rx_data,
    output reg          rx_done,
    output reg          rx_valid,
    output reg          rx_crc_err,
    output reg          rx_stuff_err
);
    localparam IDLE=4'd0, DYN=4'd1, CRC_LEAD=4'd2, CRC_SEQ=4'd3, TAIL=4'd4, DONE=4'd5;
    reg [3:0] state;

    reg [9:0]  raw_idx;
    reg [9:0]  raw_total_r;
    reg [2:0]  run_len;
    reg        run_bit;
    reg        expect_stuff;
    reg [2:0]  dyn;
    reg [3:0]  dlc_shift;
    reg        brs_seen;
    reg        form_err;

    reg [16:0] crc17;
    reg [20:0] crc21;
    reg [20:0] crc_rx;
    reg [4:0]  seq_idx;
    reg [2:0]  grp_cnt;
    reg [3:0]  tail_idx;

    // CRC-21 is used for 20 or more payload bytes, i.e. DLC >= 11.
    wire is_crc21  = (rx_dlc >= 4'd11);
    wire [4:0] cw  = is_crc21 ? 5'd21 : 5'd17;
    wire [20:0] crc_mask = is_crc21 ? 21'h1FFFFF : 21'h01FFFF;
    wire [20:0] crc_calc = is_crc21 ? crc21 : {4'd0, crc17};

    wire [9:0] dpos = raw_idx - 10'd22;

    function [16:0] crc17_step(input [16:0] c, input b);
        reg m; reg [16:0] sh;
        begin
            m  = c[16];
            sh = {c[15:0], 1'b0};
            crc17_step = (m ^ b) ? (sh ^ 17'h1685B) : sh;
        end
    endfunction

    function [20:0] crc21_step(input [20:0] c, input b);
        reg m; reg [20:0] sh;
        begin
            m  = c[20];
            sh = {c[19:0], 1'b0};
            crc21_step = (m ^ b) ? (sh ^ 21'h102899) : sh;
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

    // Receiver drives the ACK slot dominant.
    assign rx_ack = (state == TAIL && tail_idx == 4'd1) ? 1'b0 : 1'b1;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state <= IDLE;
            rx_done <= 1'b0; rx_valid <= 1'b0;
            rx_crc_err <= 1'b0; rx_stuff_err <= 1'b0; form_err <= 1'b0;
            raw_idx <= 10'd0; raw_total_r <= 10'd22;
            run_len <= 3'd0; run_bit <= 1'b1; expect_stuff <= 1'b0;
            dyn <= 3'd0; dlc_shift <= 4'd0; brs_seen <= 1'b0;
            crc17 <= 17'd0; crc21 <= 21'd0; crc_rx <= 21'd0;
            seq_idx <= 5'd0; grp_cnt <= 3'd0; tail_idx <= 4'd0;
            rx_id <= 11'd0; rx_dlc <= 4'd0; rx_data <= 512'd0;
        end else begin
            rx_done  <= 1'b0;
            rx_valid <= 1'b0;

            case (state)
                IDLE: begin
                    if (rx_bit == 1'b0) begin
                        // SOF is consumed here.
                        crc17 <= crc17_step(17'h10000,  1'b0);
                        crc21 <= crc21_step(21'h100000, 1'b0);
                        raw_idx      <= 10'd1;
                        raw_total_r  <= 10'd22;
                        run_len      <= 3'd1;
                        run_bit      <= 1'b0;
                        expect_stuff <= 1'b0;
                        dyn          <= 3'd0;
                        dlc_shift    <= 4'd0;
                        crc_rx       <= 21'd0;
                        seq_idx      <= 5'd0;
                        grp_cnt      <= 3'd0;
                        tail_idx     <= 4'd0;
                        rx_crc_err   <= 1'b0;
                        rx_stuff_err <= 1'b0;
                        form_err     <= 1'b0;
                        rx_id        <= 11'd0;
                        rx_dlc       <= 4'd0;
                        rx_data      <= 512'd0;
                        state        <= DYN;
                    end
                end

                DYN: begin
                    if (expect_stuff) begin
                        // Dynamic stuff bit: check polarity, do not store it as
                        // payload and do not advance raw_idx, but DO feed it into
                        // the CRC. ISO computes the CRC over the STUFFED stream,
                        // which is exactly why the stuff count field exists.
                        if (rx_bit != ~run_bit) rx_stuff_err <= 1'b1;
                        crc17        <= crc17_step(crc17, rx_bit);
                        crc21        <= crc21_step(crc21, rx_bit);
                        dyn          <= dyn + 3'd1;
                        run_bit      <= rx_bit;
                        run_len      <= 3'd1;
                        expect_stuff <= 1'b0;
                    end else begin
                        crc17 <= crc17_step(crc17, rx_bit);
                        crc21 <= crc21_step(crc21, rx_bit);

                        if (raw_idx <= 10'd11)
                            rx_id[4'd11 - raw_idx[3:0]] <= rx_bit;
                        else if (raw_idx == 10'd16)
                            brs_seen <= rx_bit;
                        else if (raw_idx >= 10'd18 && raw_idx <= 10'd21) begin
                            // DLC arrives MSB first at raw_idx 18..21.
                            // Explicit decode: constant indices, no width math.
                            case (raw_idx[1:0])
                                2'd2: rx_dlc[3] <= rx_bit;  // raw_idx 18
                                2'd3: rx_dlc[2] <= rx_bit;  // raw_idx 19
                                2'd0: rx_dlc[1] <= rx_bit;  // raw_idx 20
                                2'd1: rx_dlc[0] <= rx_bit;  // raw_idx 21
                            endcase
                            dlc_shift <= {dlc_shift[2:0], rx_bit};
                        end
                        else if (raw_idx >= 10'd22)
                            rx_data[9'd511 - dpos[8:0]] <= rx_bit;

                        if (rx_bit == run_bit) begin
                            run_len <= run_len + 3'd1;
                            if (run_len == 3'd4) expect_stuff <= 1'b1;
                        end else begin
                            run_bit <= rx_bit;
                            run_len <= 3'd1;
                        end

                        raw_idx <= raw_idx + 10'd1;

                        if (raw_idx == 10'd21) begin
                            // Last DLC bit: payload length becomes known.
                            raw_total_r <= 10'd22 +
                                ({3'd0, dlc_bytes({dlc_shift[2:0], rx_bit})} << 3);
                            if (dlc_bytes({dlc_shift[2:0], rx_bit}) == 7'd0)
                                state <= CRC_LEAD;
                        end else if (raw_idx >= 10'd22 &&
                                     (raw_idx + 10'd1) == raw_total_r) begin
                            state <= CRC_LEAD;
                        end
                    end
                end

                CRC_LEAD: begin
                    // Leading fixed stuff bit. Always present, never counted
                    // in the stuff count, never fed into the CRC.
                    seq_idx <= 5'd0;
                    grp_cnt <= 3'd0;
                    state   <= CRC_SEQ;
                end

                CRC_SEQ: begin
                    if (grp_cnt == 3'd4) begin
                        // Fixed stuff bit before the next 4-bit group.
                        grp_cnt <= 3'd0;
                    end else begin
                        if (seq_idx < 5'd4) begin
                            // Stuff count bits ARE part of the CRC input.
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

                TAIL: begin
                    if (tail_idx == 4'd0) begin
                        // CRC delimiter; crc_rx has settled by this cycle.
                        if (rx_bit != 1'b1) form_err <= 1'b1;
                        if ((crc_rx & crc_mask) != (crc_calc & crc_mask))
                            rx_crc_err <= 1'b1;
                    end else if (tail_idx >= 4'd2) begin
                        // ACK delimiter and EOF must be recessive.
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
