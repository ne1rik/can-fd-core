`timescale 1ns/1ps

// CAN FD Bit Timing Controller (ISO 11898-1:2015)
//
// Manages two-phase bit timing:
//   - Nominal Bit Time (NBT): arbitration phase, typically 500 kbps
//   - Data Bit Time (DBT):    data phase when BRS=1, typically 2/5/8 Mbps
//
// Each bit time is divided into three segments:
//   SYNC (1 tick) + TSEG1 (before sample point) + TSEG2 (after sample point)
//
// Sample point is at (1 + TSEG1) / (1 + TSEG1 + TSEG2) of the bit time.
//
// SSP (Secondary Sample Point) offset compensates for transceiver propagation
// delay in the data phase: RX samples the bus SSP_OFFSET ticks after the
// nominal sample point. Exported via ssp_sample_en output.
//
// Assumption: system clock period = 10 ns (100 MHz). Bit times reported
// in ns are integer multiples of this. Adjust CLK_PERIOD_NS if different.
module can_bit_timing #(
    // Nominal Bit Time parameters (arbitration phase)
    parameter int NBT_PRESCALER = 1,
    parameter int NBT_TSEG1     = 12,
    parameter int NBT_TSEG2     = 4,

    // Data Bit Time parameters (data phase, BRS=1)
    parameter int DBT_PRESCALER = 1,
    parameter int DBT_TSEG1     = 3,
    parameter int DBT_TSEG2     = 1,

    // SSP offset in system clock cycles (data phase only)
    parameter int SSP_OFFSET    = 0,

    // System clock period in ns (integer). Used only for reporting.
    parameter int CLK_PERIOD_NS = 10
)(
    input  wire        clk,
    input  wire        rst_n,
    input  wire        brs_active,  // 1 = data phase (BRS=1), 0 = nominal
    input  wire        sync_edge,   // Resync request (SOF falling edge, etc.)

    output wire [15:0] current_bit_time_ns,  // Duration of current bit in ns
    output reg         sample_en,            // Pulse at nominal sample point
    output reg         bit_boundary,         // Pulse at end of bit
    output wire        phase,                // 0 = nominal, 1 = data
    output wire [7:0]  ssp_offset_cycles,    // SSP delay in cycles
    output wire        ssp_sample_en         // Pulse at SSP-adjusted sample
);

    assign phase = brs_active;
    assign ssp_offset_cycles = SSP_OFFSET[7:0];

    // Bit time in ticks: 1 (SYNC) + TSEG1 + TSEG2
    // In ns: ticks * prescaler * CLK_PERIOD_NS (all integer)
    wire [15:0] nbt_ticks = 16'd1 + NBT_TSEG1[15:0] + NBT_TSEG2[15:0];
    wire [15:0] dbt_ticks = 16'd1 + DBT_TSEG1[15:0] + DBT_TSEG2[15:0];

    wire [15:0] nbt_ns = (NBT_PRESCALER[15:0] * nbt_ticks) * CLK_PERIOD_NS[15:0];
    wire [15:0] dbt_ns = (DBT_PRESCALER[15:0] * dbt_ticks) * CLK_PERIOD_NS[15:0];

    assign current_bit_time_ns = brs_active ? dbt_ns : nbt_ns;

    // Active parameters switched by brs_active
    wire [7:0] active_prescaler = brs_active ? DBT_PRESCALER[7:0] : NBT_PRESCALER[7:0];
    wire [7:0] active_tseg1     = brs_active ? DBT_TSEG1[7:0]     : NBT_TSEG1[7:0];
    wire [7:0] active_tseg2     = brs_active ? DBT_TSEG2[7:0]     : NBT_TSEG2[7:0];

    wire [8:0] total_ticks  = 9'd1 + {1'b0, active_tseg1} + {1'b0, active_tseg2};
    wire [8:0] sample_tick  = 9'd1 + {1'b0, active_tseg1};

    // Clock prescaler counter
    reg [7:0] clk_cnt;
    wire tick_en = (clk_cnt == active_prescaler - 8'd1);

    // Bit timing counter
    reg [8:0] tseg_cnt;

    // SSP shift register: delayed sample_en pulses
    reg [15:0] ssp_shift;

    // SSP-adjusted sample enable
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

            // Clock prescaler
            if (clk_cnt == active_prescaler - 8'd1) begin
                clk_cnt <= 8'd0;
            end else begin
                clk_cnt <= clk_cnt + 8'd1;
            end

            // SSP shift register (always shift on tick)
            if (tick_en) begin
                ssp_shift <= {ssp_shift[14:0], sample_en};
            end

            // Bit timing counter
            if (tick_en) begin
                if (sync_edge) begin
                    // Resync: restart bit from tick 0
                    tseg_cnt <= 9'd0;
                end else if (tseg_cnt == total_ticks - 9'd1) begin
                    bit_boundary <= 1'b1;
                    tseg_cnt <= 9'd0;
                end else begin
                    tseg_cnt <= tseg_cnt + 9'd1;
                end

                if (tseg_cnt == sample_tick) begin
                    sample_en <= 1'b1;
                end
            end
        end
    end

endmodule
