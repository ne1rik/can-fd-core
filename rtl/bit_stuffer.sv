`timescale 1ns / 1ps

module bit_stuffer (
    input  wire       clk,
    input  wire       rst_n,
    
    input  wire       data_in,
    input  wire       data_in_valid,
    
    output reg        data_out,
    output reg        data_out_valid,
    output reg [7:0]  stuff_count
);

    reg [2:0] consecutive_count;
    reg       last_bit;
    reg       need_stuff_bit;
    reg       first_bit;
    
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            data_out <= 1'b1;
            data_out_valid <= 1'b0;
            stuff_count <= 8'd0;
            consecutive_count <= 3'd0;
            last_bit <= 1'b0;
            need_stuff_bit <= 1'b0;
            first_bit <= 1'b1;
        end else if (need_stuff_bit) begin
            data_out <= ~last_bit;
            data_out_valid <= 1'b1;
            stuff_count <= stuff_count + 1;
            consecutive_count <= 3'd1;
            last_bit <= ~last_bit;
            need_stuff_bit <= 1'b0;
        end else if (data_in_valid) begin
            data_out <= data_in;
            data_out_valid <= 1'b1;
            
            if (first_bit) begin
                last_bit <= data_in;
                consecutive_count <= 3'd1;
                first_bit <= 1'b0;
            end else if (data_in == last_bit) begin
                // ПРАВИЛЬНАЯ ЛОГИКА: проверяем ДО инкремента
                if (consecutive_count == 3'd4) begin
                    need_stuff_bit <= 1'b1;
                end
                consecutive_count <= consecutive_count + 1;
            end else begin
                consecutive_count <= 3'd1;
                last_bit <= data_in;
            end
        end else begin
            data_out_valid <= 1'b0;
        end
    end

endmodule
