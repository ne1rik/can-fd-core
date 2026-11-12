`timescale 1ns / 1ps

module crc17_canfd (
    input  wire        clk,
    input  wire        rst_n,
    input  wire        data_in,
    input  wire        data_in_valid,
    input  wire        crc_reset,
    output wire [16:0] crc_out
);

    localparam [16:0] POLY = 17'h1685B;
    localparam [16:0] MASK = 17'h1FFFF;

    reg  [16:0] crc_reg;
    wire [16:0] shifted;

    assign shifted = (crc_reg << 1) & MASK;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            crc_reg <= 17'h00000;
        end else if (crc_reset) begin
            crc_reg <= 17'h00000;
        end else if (data_in_valid) begin
            if (crc_reg[16] ^ data_in)
                crc_reg <= shifted ^ POLY;
            else
                crc_reg <= shifted;
        end
    end

    assign crc_out = crc_reg;

endmodule
