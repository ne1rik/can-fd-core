`timescale 1ns/1ps
module can_fd_tx #(
    parameter int EXTENDED = 0,
    parameter int CLASSIC  = 0
)(
    input  wire         clk, rst_n,
    input  wire         tx_start,
    input  wire [28:0]  tx_id,
    input  wire [3:0]   tx_dlc,
    input  wire [511:0] tx_data,
    input  wire         tx_brs,
    output reg          tx_bit,
    output reg          tx_bit_valid,
    output wire         tx_done,
    output wire         tx_busy
);
    wire is_ext = (EXTENDED != 0);
    wire is_cls = (CLASSIC != 0);

    localparam IDLE=4'd0, F_RAW=4'd1, F_STUFF=4'd2, F_FSB1=4'd3, F_SC=4'd4,
               F_CRC=4'd5, F_TAIL=4'd6, F_SHIFT=4'd7, DONE=4'd8,
               C_CRC_APP=4'd9, C_STUFF=4'd10, C_STUFF_BIT=4'd11;
    reg [3:0] state;

    reg [28:0]  id_reg;
    reg [3:0]   dlc_reg;
    reg [511:0] data_reg;
    reg         brs_reg;

    reg frame_buf [0:1100];
    reg raw_buf   [0:1100];
    reg [10:0] wr_len, rd_idx, raw_idx;
    reg [10:0] c_rd_idx, c_rd_len;
    reg        c_last;
    reg [2:0]  run_cnt;
    reg        run_bit;
    reg [2:0]  dyn;
    reg [20:0] crc_reg, crc_final;
    reg [14:0] c_crc;
    reg [3:0]  c_crc_idx;
    reg [1:0]  sc_idx;
    reg [4:0]  crc_idx;
    reg [2:0]  grp;
    reg [3:0]  tail_idx;

    wire is_crc21 = (dlc_reg >= 4'd11);
    wire [4:0]  cw    = is_crc21 ? 5'd21 : 5'd17;
    wire [20:0] poly  = is_crc21 ? 21'h102899 : 21'h1685B;
    wire [20:0] cmask = is_crc21 ? 21'h1FFFFF : 21'h1FFFF;

    function [20:0] crc_step(input [20:0] c, input b);
        reg m; reg [20:0] sh;
        begin
            m = is_crc21 ? c[20] : c[16];
            sh = (c << 1) & cmask;
            crc_step = (m ^ b) ? (sh ^ poly) : sh;
        end
    endfunction

    function [14:0] c_crc_step(input [14:0] c, input b);
        reg m; reg [14:0] sh;
        begin
            m = c[14];
            sh = {c[13:0], 1'b0};
            c_crc_step = (m ^ b) ? (sh ^ 15'h4599) : sh;
        end
    endfunction

    reg [6:0] data_bytes;
    always @* begin
        case (dlc_reg)
            4'd0,4'd1,4'd2,4'd3,4'd4,4'd5,4'd6,4'd7,4'd8: data_bytes = {3'd0, dlc_reg};
            4'd9:  data_bytes = 7'd12;
            4'd10: data_bytes = 7'd16;
            4'd11: data_bytes = 7'd20;
            4'd12: data_bytes = 7'd24;
            4'd13: data_bytes = 7'd32;
            4'd14: data_bytes = 7'd48;
            4'd15: data_bytes = 7'd64;
            default: data_bytes = 7'd0;
        endcase
    end

    wire [6:0] pay_bytes = (is_cls && data_bytes > 7'd8) ? 7'd8 : data_bytes;

    wire [10:0] header_len = is_cls ? (is_ext ? 11'd39 : 11'd19)
                                    : (is_ext ? 11'd41 : 11'd22);
    wire [10:0] dlc_base  = header_len - 11'd4;
    wire [10:0] raw_total = header_len + ({4'd0, pay_bytes} << 3);

    wire [2:0] gray = dyn ^ (dyn >> 1);
    wire [3:0] sc_field = {gray, gray[2] ^ gray[1] ^ gray[0]};

    wire [8:0] dpos     = raw_idx[8:0] - header_len[8:0];
    wire [8:0] data_idx = 9'd511 - dpos;

    reg raw_bit;
    always @* begin
        raw_bit = 1'b0;
        if (raw_idx == 11'd0) begin
            raw_bit = 1'b0;
        end else if (is_ext) begin
            if (raw_idx <= 11'd11)      raw_bit = id_reg[5'd29 - raw_idx[4:0]];
            else if (raw_idx == 11'd12) raw_bit = 1'b1;
            else if (raw_idx == 11'd13) raw_bit = 1'b1;
            else if (raw_idx <= 11'd31) raw_bit = id_reg[5'd31 - raw_idx[4:0]];
            else if (raw_idx == 11'd32) raw_bit = 1'b0;
            else if (raw_idx == 11'd33) raw_bit = is_cls ? 1'b0 : 1'b1;
            else if (raw_idx == 11'd34) raw_bit = 1'b0;
            else if (!is_cls && raw_idx == 11'd35) raw_bit = brs_reg;
            else if (!is_cls && raw_idx == 11'd36) raw_bit = 1'b0;
            else begin
                case (raw_idx - dlc_base)
                    11'd0:   raw_bit = dlc_reg[3];
                    11'd1:   raw_bit = dlc_reg[2];
                    11'd2:   raw_bit = dlc_reg[1];
                    default: raw_bit = dlc_reg[0];
                endcase
            end
        end else begin
            if (raw_idx <= 11'd11)      raw_bit = id_reg[5'd11 - raw_idx[4:0]];
            else if (raw_idx == 11'd12) raw_bit = 1'b0;
            else if (raw_idx == 11'd13) raw_bit = 1'b0;
            else if (raw_idx == 11'd14) raw_bit = is_cls ? 1'b0 : 1'b1;
            else if (!is_cls && raw_idx == 11'd15) raw_bit = 1'b0;
            else if (!is_cls && raw_idx == 11'd16) raw_bit = brs_reg;
            else if (!is_cls && raw_idx == 11'd17) raw_bit = 1'b0;
            else begin
                case (raw_idx - dlc_base)
                    11'd0:   raw_bit = dlc_reg[3];
                    11'd1:   raw_bit = dlc_reg[2];
                    11'd2:   raw_bit = dlc_reg[1];
                    default: raw_bit = dlc_reg[0];
                endcase
            end
        end
        if (raw_idx >= header_len) raw_bit = data_reg[data_idx];
    end

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state <= IDLE; tx_bit <= 1'b1; tx_bit_valid <= 1'b0;
            wr_len <= 0; rd_idx <= 0; raw_idx <= 0;
            c_rd_idx <= 0; c_rd_len <= 0; c_last <= 1'b0;
            run_cnt <= 0; run_bit <= 1'b0; dyn <= 0;
            crc_reg <= 0; crc_final <= 0; c_crc <= 0; c_crc_idx <= 0;
            sc_idx <= 0; crc_idx <= 0; grp <= 0; tail_idx <= 0;
        end else begin
            tx_bit_valid <= 1'b0;
            case (state)
                IDLE: if (tx_start) begin
                    id_reg <= tx_id; dlc_reg <= tx_dlc;
                    data_reg <= tx_data; brs_reg <= tx_brs;
                    wr_len <= 0; raw_idx <= 0; run_cnt <= 0; dyn <= 0;
                    tail_idx <= 0; c_crc <= 15'd0; c_crc_idx <= 4'd0;
                    crc_reg <= (tx_dlc >= 4'd11) ? 21'h100000 : 21'h010000;
                    state <= F_RAW;
                end

                F_RAW: begin
                    if (is_cls) begin
                        raw_buf[raw_idx] <= raw_bit;
                        c_crc <= c_crc_step(c_crc, raw_bit);
                        raw_idx <= raw_idx + 11'd1;
                        if (raw_idx + 11'd1 == raw_total) begin
                            c_crc_idx <= 4'd0;
                            state <= C_CRC_APP;
                        end
                    end else begin
                        frame_buf[wr_len] <= raw_bit;
                        wr_len <= wr_len + 11'd1;
                        crc_reg <= crc_step(crc_reg, raw_bit);
                        if (raw_idx + 11'd1 == raw_total) begin
                            state <= F_FSB1;
                        end else begin
                            if (run_cnt != 0 && raw_bit == run_bit && run_cnt == 3'd4) begin
                                run_bit <= ~raw_bit;
                                run_cnt <= 3'd1;
                                raw_idx <= raw_idx + 11'd1;
                                state <= F_STUFF;
                            end else begin
                                if (run_cnt == 0 || raw_bit != run_bit) begin
                                    run_bit <= raw_bit; run_cnt <= 3'd1;
                                end else run_cnt <= run_cnt + 3'd1;
                                raw_idx <= raw_idx + 11'd1;
                            end
                        end
                    end
                end

                F_STUFF: begin
                    frame_buf[wr_len] <= run_bit;
                    wr_len <= wr_len + 11'd1;
                    crc_reg <= crc_step(crc_reg, run_bit);
                    dyn <= dyn + 3'd1;
                    state <= F_RAW;
                end

                F_FSB1: begin
                    frame_buf[wr_len] <= ~frame_buf[wr_len - 11'd1];
                    wr_len <= wr_len + 11'd1;
                    sc_idx <= 2'd0;
                    state <= F_SC;
                end

                F_SC: begin
                    frame_buf[wr_len] <= sc_field[2'd3 - sc_idx];
                    wr_len <= wr_len + 11'd1;
                    crc_reg <= crc_step(crc_reg, sc_field[2'd3 - sc_idx]);
                    if (sc_idx == 2'd3) begin
                        crc_final <= crc_step(crc_reg, sc_field[2'd3 - sc_idx]);
                        crc_idx <= 5'd0; grp <= 3'd0;
                        state <= F_CRC;
                    end else sc_idx <= sc_idx + 2'd1;
                end

                F_CRC: begin
                    if (grp == 3'd0) begin
                        frame_buf[wr_len] <= ~frame_buf[wr_len - 11'd1];
                        wr_len <= wr_len + 11'd1;
                        grp <= 3'd1;
                    end else begin
                        frame_buf[wr_len] <= crc_final[cw - 5'd1 - crc_idx];
                        wr_len <= wr_len + 11'd1;
                        crc_idx <= crc_idx + 5'd1;
                        if ((crc_idx + 5'd1) == cw) begin
                            tail_idx <= 4'd0;
                            state <= F_TAIL;
                        end else grp <= (grp == 3'd4) ? 3'd0 : grp + 3'd1;
                    end
                end

                C_CRC_APP: begin
                    raw_buf[raw_idx] <= c_crc[4'd14 - c_crc_idx];
                    raw_idx <= raw_idx + 11'd1;
                    if (c_crc_idx == 4'd14) begin
                        c_rd_len <= raw_idx + 11'd1;
                        c_rd_idx <= 11'd0;
                        wr_len   <= 11'd0;
                        run_cnt  <= 3'd0;
                        run_bit  <= 1'b0;
                        state <= C_STUFF;
                    end else c_crc_idx <= c_crc_idx + 4'd1;
                end

                C_STUFF: begin
                    if (c_rd_idx >= c_rd_len) begin
                        tail_idx <= 4'd0;
                        state <= F_TAIL;
                    end else begin
                        c_last <= raw_buf[c_rd_idx];
                        frame_buf[wr_len] <= raw_buf[c_rd_idx];
                        wr_len   <= wr_len + 11'd1;
                        c_rd_idx <= c_rd_idx + 11'd1;
                        if (run_cnt != 0 && raw_buf[c_rd_idx] == run_bit && run_cnt == 3'd4) begin
                            run_bit <= ~raw_buf[c_rd_idx];
                            run_cnt <= 3'd1;
                            state <= C_STUFF_BIT;
                        end else begin
                            if (run_cnt == 0 || raw_buf[c_rd_idx] != run_bit) begin
                                run_bit <= raw_buf[c_rd_idx];
                                run_cnt <= 3'd1;
                            end else run_cnt <= run_cnt + 3'd1;
                        end
                    end
                end

                C_STUFF_BIT: begin
                    frame_buf[wr_len] <= ~c_last;
                    wr_len <= wr_len + 11'd1;
                    state <= C_STUFF;
                end

                F_TAIL: begin
                    frame_buf[wr_len] <= 1'b1;
                    wr_len <= wr_len + 11'd1;
                    if (tail_idx == 4'd9) begin
                        rd_idx <= 11'd0;
                        tail_idx <= 4'd0;
                        state <= F_SHIFT;
                    end else tail_idx <= tail_idx + 4'd1;
                end

                F_SHIFT: begin
                    if (rd_idx < wr_len) begin
                        tx_bit <= frame_buf[rd_idx];
                        tx_bit_valid <= 1'b1;
                        rd_idx <= rd_idx + 11'd1;
                    end else state <= DONE;
                end

                DONE: state <= IDLE;
                default: state <= IDLE;
            endcase
        end
    end

    assign tx_done = (state == DONE);
    assign tx_busy = (state != IDLE) && (state != DONE);
endmodule
