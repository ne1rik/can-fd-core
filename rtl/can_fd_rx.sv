`timescale 1ns/1ps

module can_fd_rx (
    input  wire         clk, rst_n,
    input  wire         rx_bit,
    output reg          rx_ack,
    output reg [10:0]   rx_id,
    output reg [3:0]    rx_dlc,
    output reg [511:0]  rx_data,
    output reg          rx_done,
    output reg          rx_valid,
    output reg          rx_crc_err,
    output reg          rx_stuff_err
);

    localparam IDLE=0, ARB_ID=1, CTRL=2, DLC_S=3, DATA=4, CRC=5, ACK_S=6, EOF=7, DONE=8;
    
    reg [3:0] state;
    reg [9:0] bit_cnt;
    reg [2:0] stuff_cnt;
    reg [2:0] dyn_stuff_cnt;
    reg [20:0] crc_reg;
    reg [6:0] data_bytes;
    reg [9:0] data_bit_cnt;
    reg brs_seen;
    reg last_bit;
    
    wire is_crc21 = (data_bytes > 7'd16);
    wire [4:0] cw = is_crc21 ? 5'd21 : 5'd17;
    wire [20:0] poly = is_crc21 ? 21'h102899 : 21'h1685B;
    wire [20:0] cmask = is_crc21 ? 21'h1FFFFF : 21'h1FFFF;
    
    function [20:0] crc_step(input [20:0] c, input b);
        reg m; reg [20:0] sh;
        begin
            m = is_crc21 ? c[20] : c[16];
            sh = (c<<1) & cmask;
            crc_step = (m^b) ? (sh^poly) : sh;
        end
    endfunction
    
    always @* begin
        case (rx_dlc)
            0,1,2,3,4,5,6,7,8: data_bytes = {3'd0, rx_dlc};
            9: data_bytes = 7'd12;
            10: data_bytes = 7'd16;
            11: data_bytes = 7'd20;
            12: data_bytes = 7'd24;
            13: data_bytes = 7'd32;
            14: data_bytes = 7'd48;
            15: data_bytes = 7'd64;
            default: data_bytes = 7'd0;
        endcase
    end
    
    wire [9:0] data_bits_total = {3'b0, data_bytes} << 3;
    
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state <= IDLE;
            rx_ack <= 1'b1;
            rx_done <= 1'b0;
            rx_valid <= 1'b0;
            rx_crc_err <= 1'b0;
            rx_stuff_err <= 1'b0;
            bit_cnt <= 0;
            stuff_cnt <= 0;
            dyn_stuff_cnt <= 0;
            crc_reg <= 0;
            brs_seen <= 0;
            last_bit <= 1'b1;
            data_bit_cnt <= 0;
        end else begin
            rx_done <= 1'b0;
            rx_valid <= 1'b0;
            
            case (state)
                IDLE: begin
                    if (rx_bit == 1'b0) begin
                        state <= ARB_ID;
                        crc_reg <= 21'h010000;
                        dyn_stuff_cnt <= 0;
                        stuff_cnt <= 3'd1;
                        last_bit <= 1'b0;
                        bit_cnt <= 10'd0;
                    end
                end
                
                ARB_ID: begin
                    // 11 бит ID: индексы от 10 до 0
                    rx_id[10 - bit_cnt[3:0]] <= rx_bit;
                    crc_reg <= crc_step(crc_reg, rx_bit);
                    
                    if (rx_bit == last_bit) begin
                        if (stuff_cnt == 3'd4) stuff_cnt <= 3'd0;
                        else stuff_cnt <= stuff_cnt + 1;
                    end else begin
                        stuff_cnt <= 3'd1;
                    end
                    last_bit <= rx_bit;
                    
                    if (bit_cnt == 10'd10) begin
                        state <= CTRL;
                        bit_cnt <= 10'd0;
                    end else begin
                        bit_cnt <= bit_cnt + 1;
                    end
                end
                
                CTRL: begin
                    if (bit_cnt[2:0] == 3'd4) brs_seen <= rx_bit;
                    crc_reg <= crc_step(crc_reg, rx_bit);
                    
                    if (rx_bit == last_bit) begin
                        if (stuff_cnt == 3'd4) stuff_cnt <= 3'd0;
                        else stuff_cnt <= stuff_cnt + 1;
                    end else begin
                        stuff_cnt <= 3'd1;
                    end
                    last_bit <= rx_bit;
                    
                    if (bit_cnt == 10'd5) begin
                        state <= DLC_S;
                        bit_cnt <= 10'd0;
                    end else begin
                        bit_cnt <= bit_cnt + 1;
                    end
                end
                
                DLC_S: begin
                    rx_dlc[3 - bit_cnt[1:0]] <= rx_bit;
                    crc_reg <= crc_step(crc_reg, rx_bit);
                    
                    if (rx_bit == last_bit) begin
                        if (stuff_cnt == 3'd4) stuff_cnt <= 3'd0;
                        else stuff_cnt <= stuff_cnt + 1;
                    end else begin
                        stuff_cnt <= 3'd1;
                    end
                    last_bit <= rx_bit;
                    
                    if (bit_cnt == 10'd3) begin
                        state <= DATA;
                        bit_cnt <= 10'd0;
                        data_bit_cnt <= 10'd0;
                    end else begin
                        bit_cnt <= bit_cnt + 1;
                    end
                end
                
                DATA: begin
                    if (stuff_cnt == 3'd5) begin
                        if (rx_bit != ~last_bit) rx_stuff_err <= 1'b1;
                        dyn_stuff_cnt <= dyn_stuff_cnt + 1;
                        stuff_cnt <= 3'd1;
                        last_bit <= rx_bit;
                    end else begin
                        rx_data[511 - data_bit_cnt] <= rx_bit;
                        crc_reg <= crc_step(crc_reg, rx_bit);
                        data_bit_cnt <= data_bit_cnt + 1;
                        
                        if (rx_bit == last_bit) stuff_cnt <= stuff_cnt + 1;
                        else stuff_cnt <= 3'd1;
                        last_bit <= rx_bit;
                        
                        if (data_bit_cnt + 1 == data_bits_total) begin
                            state <= CRC;
                            bit_cnt <= 10'd0;
                        end
                    end
                end
                
                CRC: begin
                    if (bit_cnt == 0) begin
                        last_bit <= rx_bit;
                        bit_cnt <= bit_cnt + 1;
                    end else begin
                        if ((bit_cnt % 5) == 0) begin
                            last_bit <= rx_bit;
                            bit_cnt <= bit_cnt + 1;
                        end else begin
                            crc_reg <= crc_step(crc_reg, rx_bit);
                            last_bit <= rx_bit;
                            bit_cnt <= bit_cnt + 1;
                            
                            // Исправлено расширение ширины для Verilator
                            if (bit_cnt == ({5'd0, cw} + 10'd4)) begin
                                state <= ACK_S;
                                bit_cnt <= 10'd0;
                            end
                        end
                    end
                end
                
                ACK_S: begin
                    rx_ack <= 1'b0;
                    state <= EOF;
                    bit_cnt <= 10'd0;
                end
                
                EOF: begin
                    rx_ack <= 1'b1;
                    if (bit_cnt == 10'd6) begin
                        state <= DONE;
                    end else begin
                        bit_cnt <= bit_cnt + 1;
                    end
                end
                
                DONE: begin
                    rx_done <= 1'b1;
                    rx_valid <= ~rx_crc_err & ~rx_stuff_err;
                    state <= IDLE;
                end
                
                default: state <= IDLE;
            endcase
        end
    end
endmodule
