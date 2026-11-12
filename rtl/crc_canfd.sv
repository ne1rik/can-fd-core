`timescale 1ns / 1ps

module crc_canfd #(
    parameter CRC_WIDTH = 17  // 17 для payload <= 16 байт, 21 для >= 20 байт
)(
    input  wire              clk,
    input  wire              rst_n,
    
    input  wire              data_in,
    input  wire              data_in_valid,
    input  wire              crc_reset,
    
    output wire [CRC_WIDTH-1:0] crc_out
);

    // CRC-17: x^17 + x^16 + x^14 + x^13 + x^11 + x^6 + x^4 + x^3 + x + 1 = 0x1685B
    // CRC-21: x^21 + x^20 + x^15 + x^13 + x^12 + x^11 + x^9 + x^7 + x^4 + x^3 + 1 = 0x102899
    localparam [20:0] POLY_17 = 21'h1685B;
    localparam [20:0] POLY_21 = 21'h102899;
    
    reg [CRC_WIDTH-1:0] crc_reg;
    wire [CRC_WIDTH-1:0] shifted;
    wire [20:0] poly;
    
    assign poly = (CRC_WIDTH == 17) ? POLY_17 : POLY_21;
    assign shifted = (crc_reg << 1) & ((1 << CRC_WIDTH) - 1);
    
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            crc_reg <= {CRC_WIDTH{1'b0}};
        end else if (crc_reset) begin
            crc_reg <= {CRC_WIDTH{1'b0}};
        end else if (data_in_valid) begin
            if (crc_reg[CRC_WIDTH-1] ^ data_in)
                crc_reg <= shifted ^ poly[CRC_WIDTH-1:0];
            else
                crc_reg <= shifted;
        end
    end
    
    assign crc_out = crc_reg;

endmodule
