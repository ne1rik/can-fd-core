// Minimal formal probe: a saturating counter that must never exceed 3.
module smoke_formal (
    input wire clk,
    input wire rst
);
    reg [1:0] cnt;

    always @(posedge clk) begin
        if (rst)
            cnt <= 2'd0;
        else if (cnt < 2'd3)
            cnt <= cnt + 2'd1;
    end

`ifdef FORMAL
    always @(posedge clk) begin
        if (!rst)
            assert (cnt <= 2'd3);
    end
`endif
endmodule
