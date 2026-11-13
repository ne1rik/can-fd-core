// Minimal design used only to probe Verilator coverage flag support.
module smoke_cov (
    input  wire clk,
    input  wire d,
    output reg  q
);
    always @(posedge clk) q <= d;
endmodule
