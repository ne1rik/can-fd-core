module dummy (
    input wire clk,
    input wire rst,
    input wire [7:0] data_in,
    output reg [7:0] data_out
);
    always @(posedge clk or posedge rst) begin
        if (rst) data_out <= 8'h00;
        else     data_out <= data_in + 8'h01;
    end
endmodule
