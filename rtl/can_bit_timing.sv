`timescale 1ns/1ps

// CAN FD bit timing controller.
//
// Bit time = SYNC(1) + TSEG1 + TSEG2 ticks; tick = prescaler system clocks.
// sample_en pulses at tick (1 + TSEG1); bit_boundary pulses at the last tick.
//
// Backward-compatibility mode: TSEG1=0 and TSEG2=0 gives a one-tick bit,
// so sample_en and bit_boundary pulse on every tick. With prescaler=1 this
// reproduces the original "one clock = one bit" behaviour exactly.
//
// SSP: ssp_sample_en is sample_en delayed by SSP_OFFSET ticks (data phase only).
module can_bit_timing #(
    parameter int NBT_PRESCALER = 1,
    parameter int NBT_TSEG1     = 0,
    parameter int NBT_TSEG2     = 0,
    parameter int DBT_PRESCALER = 1,
    parameter int DBT_TSEG1     = 0,
    parameter int DBT_TSEG2     = 0,
    parameter int SSP_OFFSET    = 0,
    parameter int CLK_PERIOD_NS = 10
)(
    input  wire        clk,
    input  wire        rst_n,
    input  wire        brs_active,
    input  wire        sync_edge,

    output wire [15:0] current_bit_time_ns,
    output reg         sample_en,
    output reg         bit_boundary,
    output wire        phase,
    output wire [7:0]  ssp_offset_cycles,
    output wire        ssp_sample_en
);
    assign phase             = brs_active;
    assign ssp_offset_cycles = SSP_OFFSET[7:0];

    wire [15:0] nbt_ticks = 16'd1 + NBT_TSEG1[15:0] + NBT_TSEG2[15:0];
    wire [15:0] dbt_ticks = 16'd1 + DBT_TSEG1[15:0] + DBT_TSEG2[15:0];

    wire [15:0] nbt_ns = (NBT_PRESCALER[15:0] * nbt_ticks) * CLK_PERIOD_NS[15:0];
    wire [15:0] dbt_ns = (DBT_PRESCALER[15:0] * dbt_ticks) * CLK_PERIOD_NS[15:0];

    assign current_bit_time_ns = brs_active ? dbt_ns : nbt_ns;

    wire [7:0] active_prescaler = brs_active ? DBT_PRESCALER[7:0] : NBT_PRESCALER[7:0];
    wire [7:0] active_tseg1     = brs_active ? DBT_TSEG1[7:0]     : NBT_TSEG1[7:0];
    wire [7:0] active_tseg2     = brs_active ? DBT_TSEG2[7:0]     : NBT_TSEG2[7:0];

    wire [8:0] total_ticks = 9'd1 + {1'b0, active_tseg1} + {1'b0, active_tseg2};
    wire [8:0] sample_tick = 9'd1 + {1'b0, active_tseg1};

    wire one_tick_bit = (active_tseg1 == 8'd0) && (active_tseg2 == 8'd0);

    reg [7:0]  clk_cnt;
    reg [8:0]  tseg_cnt;
    reg [15:0] ssp_shift;

    wire tick_en = (clk_cnt == active_prescaler - 8'd1);

    assign ssp_sample_en = (SSP_OFFSET == 0 || !brs_active)
        ? sample_en
        : ssp_shift[SSP_OFFSET];

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            clk_cnt      <= 8'd0;
            tseg_cnt     <= 9'd0;
            sample_en    <= 1'b0;
            bit_boundary <= 1'b0;
            ssp_shift    <= 16'd0;
        end else begin
            sample_en    <= 1'b0;
            bit_boundary <= 1'b0;

            if (tick_en) begin
                clk_cnt <= 8'd0;
            end else begin
                clk_cnt <= clk_cnt + 8'd1;
            end

            if (tick_en) begin
                ssp_shift <= {ssp_shift[14:0], sample_en};

                if (one_tick_bit) begin
                    sample_en    <= 1'b1;
                    bit_boundary <= 1'b1;
                    tseg_cnt     <= 9'd0;
                end else begin
                    if (tseg_cnt == sample_tick) begin
                        sample_en <= 1'b1;
                    end

                    if (sync_edge) begin
                        tseg_cnt <= 9'd0;
                    end else if (tseg_cnt == total_ticks - 9'd1) begin
                        bit_boundary <= 1'b1;
                        tseg_cnt     <= 9'd0;
                    end else begin
                        tseg_cnt <= tseg_cnt + 9'd1;
                    end
                end
            end
        end
    end
endmodule
