`timescale 1ns/1ps
module can_fd_tx #(
    parameter bit EXTENDED = 0,
    parameter bit CLASSIC  = 0
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
    localparam IDLE=0, F_RAW=1, F_STUFF=2, F_FSB1=3, F_SC=4, F_CRC=5, F_TAIL=6, F_SHIFT=7, DONE=8;
    localparam F_CRC_CALC=9, F_STUFF_ALL=10;

    reg [3:0] state;
    reg [28:0] id_reg; 
    reg [3:0] dlc_reg; 
    reg [511:0] data_reg; 
    reg brs_reg;
    
    reg frame_buf [0:1100];
    reg [10:0] wr_len, rd_idx, raw_idx;
    reg [10:0] stuff_read_end;
    reg [2:0] run_cnt; reg run_bit;
    reg [2:0] dyn;
    reg [20:0] crc_reg, crc_final;
    reg [1:0] sc_idx; reg [4:0] crc_idx; reg [2:0] grp; reg [3:0] tail_idx;
    
    reg [10:0] classic_crc_idx;
    reg [14:0] classic_crc_val;

    wire is_crc21 = (dlc_reg >= 4'd11);
    wire [4:0] cw   = is_crc21 ? 5'd21 : 5'd17;
    wire [20:0] poly  = is_crc21 ? 21'h102899 : 21'h1685B;
    wire [20:0] cmask = is_crc21 ? 21'h1FFFFF : 21'h1FFFF;
    
    wire [14:0] classic_poly = 15'h4599;
    wire [14:0] classic_cmask = 15'h7FFF;

    function [20:0] crc_step(input [20:0] c, input b);
        reg m; reg [20:0] sh;
        begin
            m = is_crc21 ? c[20] : c[16];
            sh = (c<<1) & cmask;
            crc_step = (m^b) ? (sh^poly) : sh;
        end
    endfunction
    
    function [14:0] classic_crc_step(input [14:0] c, input b);
        reg m; reg [14:0] sh;
        begin
            m = c[14];
            sh = (c<<1) & classic_cmask;
            classic_crc_step = (m^b) ? (sh^classic_poly) : sh;
        end
    endfunction

    reg [6:0] data_bytes;
    always @* begin
        case (dlc_reg)
            0,1,2,3,4,5,6,7,8: data_bytes={3'd0,dlc_reg};
            9:data_bytes=7'd12; 10:data_bytes=7'd16; 11:data_bytes=7'd20; 12:data_bytes=7'd24;
            13:data_bytes=7'd32; 14:data_bytes=7'd48; 15:data_bytes=7'd64;
            default:data_bytes=7'd0;
        endcase
    end
    
    wire [10:0] header_len = CLASSIC ? (EXTENDED ? 11'd39 : 11'd19) : (EXTENDED ? 11'd41 : 11'd22);
    wire [10:0] raw_total = header_len + ({4'b0,data_bytes}<<3);

    wire [2:0] gray = dyn ^ (dyn>>1);
    wire [3:0] sc_field = {gray, gray[2]^gray[1]^gray[0]};

    reg raw_bit;
    wire [8:0] di = raw_idx[8:0] - header_len[8:0];
    
    always @* begin
        if (raw_idx==0) raw_bit=1'b0;
        else if (raw_idx <= header_len - 1) begin
            if (EXTENDED) begin
                if (raw_idx <= 11) raw_bit = id_reg[28 - raw_idx + 1];
                else if (raw_idx == 12) raw_bit = 1'b1;
                else if (raw_idx == 13) raw_bit = 1'b1;
                else if (raw_idx <= 31) raw_bit = id_reg[31 - raw_idx];
                else if (raw_idx == 32) raw_bit = 1'b0;
                else if (raw_idx == 33) raw_bit = CLASSIC ? 1'b0 : 1'b1;
                else if (raw_idx == 34) raw_bit = 1'b0;
                else if (raw_idx == 35) raw_bit = CLASSIC ? 1'b0 : brs_reg;
                else if (raw_idx == 36) raw_bit = dlc_reg[3];
                else if (raw_idx == 37) raw_bit = dlc_reg[2];
                else if (raw_idx == 38) raw_bit = dlc_reg[1];
                else raw_bit = dlc_reg[0];
            end else begin
                if (raw_idx <= 11) raw_bit = id_reg[11 - raw_idx];
                else if (raw_idx == 12) raw_bit = 1'b0;
                else if (raw_idx == 13) raw_bit = 1'b0;
                else if (raw_idx == 14) raw_bit = CLASSIC ? 1'b0 : 1'b1;
                else if (raw_idx == 15) raw_bit = 1'b0;
                else if (raw_idx == 16) raw_bit = CLASSIC ? 1'b0 : brs_reg;
                else if (raw_idx == 17) raw_bit = CLASSIC ? 1'b0 : 1'b0;
                else if (raw_idx == 18) raw_bit = dlc_reg[3];
                else if (raw_idx == 19) raw_bit = dlc_reg[2];
                else if (raw_idx == 20) raw_bit = dlc_reg[1];
                else raw_bit = dlc_reg[0];
            end
        end
        else raw_bit = data_reg[9'd511 - di];
    end

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state <= IDLE; tx_bit <= 1'b1; tx_bit_valid <= 1'b0;
            wr_len <= 0; rd_idx <= 0; raw_idx <= 0; run_cnt <= 0; run_bit <= 0;
            dyn <= 0; crc_reg <= 0; crc_final <= 0;
            sc_idx <= 0; crc_idx <= 0; grp <= 0; tail_idx <= 0;
            classic_crc_idx <= 0; classic_crc_val <= 0;
            stuff_read_end <= 0;
        end else begin
            tx_bit_valid <= 1'b0;
            case (state)
                IDLE: if (tx_start) begin
                    id_reg <= tx_id; dlc_reg <= tx_dlc; data_reg <= tx_data; brs_reg <= tx_brs;
                    wr_len <= 0; raw_idx <= 0; run_cnt <= 0; dyn <= 0;
                    if (CLASSIC) begin
                        crc_reg <= 0;
                    end else begin
                        crc_reg <= (tx_dlc >= 4'd11) ? 21'h100000 : 21'h010000;
                    end
                    state <= F_RAW;
                end

                F_RAW: begin
                    frame_buf[wr_len] <= raw_bit; 
                    wr_len <= wr_len + 1;
                    
                    if (CLASSIC) begin
                        crc_reg <= {6'b0, classic_crc_step(crc_reg[14:0], raw_bit)};
                    end else begin
                        crc_reg <= crc_step(crc_reg, raw_bit);
                    end

                    if (raw_idx + 1 == raw_total) begin
                        if (CLASSIC) begin
                            state <= F_CRC_CALC;
                            classic_crc_idx <= 0;
                            classic_crc_val <= crc_reg[14:0];
                        end else begin
                            state <= F_FSB1;
                        end
                    end else begin
                        if (CLASSIC) begin
                            raw_idx <= raw_idx + 1;
                        end else begin
                            if (run_cnt != 0 && raw_bit == run_bit && run_cnt == 3'd4) begin
                                run_bit <= ~raw_bit;
                                run_cnt <= 3'd1;
                                raw_idx <= raw_idx + 1;
                                state <= F_STUFF;
                            end else begin
                                if (run_cnt == 0 || raw_bit != run_bit) begin run_bit <= raw_bit; run_cnt <= 3'd1; end
                                else run_cnt <= run_cnt + 1;
                                raw_idx <= raw_idx + 1;
                            end
                        end
                    end
                end

                F_STUFF: begin
                    frame_buf[wr_len] <= run_bit; wr_len <= wr_len + 1;
                    crc_reg <= crc_step(crc_reg, run_bit);
                    dyn <= dyn + 3'd1;
                    state <= F_RAW;
                end

                F_FSB1: begin
                    frame_buf[wr_len] <= ~frame_buf[wr_len-1]; wr_len <= wr_len + 1;
                    state <= F_SC; sc_idx <= 0;
                end

                F_SC: begin
                    frame_buf[wr_len] <= sc_field[2'd3-sc_idx]; wr_len <= wr_len + 1;
                    crc_reg <= crc_step(crc_reg, sc_field[2'd3-sc_idx]);
                    if (sc_idx == 2'd3) begin
                        crc_final <= crc_step(crc_reg, sc_field[2'd3-sc_idx]);
                        state <= F_CRC; crc_idx <= 0; grp <= 0;
                    end else sc_idx <= sc_idx + 1;
                end

                F_CRC: begin
                    if (grp == 0) begin
                        frame_buf[wr_len] <= ~frame_buf[wr_len-1]; wr_len <= wr_len + 1; grp <= 1;
                    end else begin
                        frame_buf[wr_len] <= crc_final[cw-1-crc_idx]; wr_len <= wr_len + 1;
                        crc_idx <= crc_idx + 1;
                        if ((crc_idx+1) == cw) state <= F_TAIL;
                        else grp <= (grp == 3'd4) ? 3'd0 : grp + 1;
                    end
                end

                F_CRC_CALC: begin
                    frame_buf[wr_len] <= classic_crc_val[14 - classic_crc_idx];
                    wr_len <= wr_len + 1;
                    if (classic_crc_idx == 14) begin
                        state <= F_STUFF_ALL;
                        raw_idx <= 0;
                        stuff_read_end <= wr_len + 1;
                        run_cnt <= 0; run_bit <= 0; dyn <= 0;
                        wr_len <= 0;
                    end else begin
                        classic_crc_idx <= classic_crc_idx + 1;
                    end
                end

                F_STUFF_ALL: begin
                    if (raw_idx < stuff_read_end) begin
                        reg current_bit;
                        current_bit = frame_buf[raw_idx];
                        frame_buf[wr_len] <= current_bit;
                        wr_len <= wr_len + 1;
                        
                        if (run_cnt != 0 && current_bit == run_bit && run_cnt == 3'd4) begin
                            run_bit <= ~current_bit;
                            run_cnt <= 3'd1;
                            // Insert stuff bit on next cycle, don't advance raw_idx yet
                            frame_buf[wr_len + 1] <= ~current_bit;
                            wr_len <= wr_len + 2;
                        end else begin
                            if (run_cnt == 0 || current_bit != run_bit) begin run_bit <= current_bit; run_cnt <= 3'd1; end
                            else run_cnt <= run_cnt + 1;
                            raw_idx <= raw_idx + 1;
                        end
                    end else begin
                        state <= F_TAIL;
                    end
                end

                F_TAIL: begin
                    frame_buf[wr_len] <= 1'b1; wr_len <= wr_len + 1;
                    if (tail_idx == 4'd9) begin state <= F_SHIFT; rd_idx <= 0; tail_idx <= 0; end
                    else tail_idx <= tail_idx + 1;
                end

                F_SHIFT: begin
                    if (rd_idx < wr_len) begin
                        tx_bit <= frame_buf[rd_idx]; tx_bit_valid <= 1'b1; rd_idx <= rd_idx + 1;
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
