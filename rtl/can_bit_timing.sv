`timescale 1ns/1ps

// CAN FD bit timing controller.
//
// Bit time = SYNC(1) + TSEG1 + TSEG2 ticks; tick = prescaler system clocks.
// sample_en pulses at tick (1 + TSEG1); bit_boundary pulses at the last tick.
//
// Backward-compatibility mode: TSEG1=0 and TSEG2=0 gives a one-tick bit, so
// both strobes pulse every tick (prescaler=1 -> one clock = one bit).
//
// Phase change (brs_active edge) RE-ALIGNS the counters. Without this the
// stale tseg_cnt can exceed the new total_ticks-1 and never match again,
// running to the 9-bit wrap (~500 clocks with no strobes).
//
// Hard sync (sync_edge) works at ANY clock phase of the prescaler. With
// prescaler > 1 a tick happens only every Nth clock, so a one-clock sync
// pulse landing on a "blind" clock (clk_cnt != prescaler-1) used to be
// dropped: the request was sampled only inside the tick_en branch, so the
// receiver missed SOF hard synchronisation whenever the edge did not
// coincide with a tick, and long frames desynchronised.
//
// The restart now happens on the sync clock itself and clears only
// tseg_cnt: the prescaler (clk_cnt) keeps its phase, so tick spacing and
// therefore the bit period stay exact, and a tick that coincides with the
// sync clock is simply the first tick of the restarted bit. With TSEG1=0
// and TSEG2=0 (one-tick-bit mode) the restart is skipped entirely: tseg_cnt
// is already 0 there, and the legacy behaviour is preserved bit-exactly.
//
// One hazard remains: a sample strobe registered by the pre-sync bit
// sequence can still fire up to one clock after the sync pulse. Together
// with the restarted cadence strobe it would put two sample strobes into
// one transmitted bit and shift the received stream by a whole bit. Such
// stale strobes are visible in the sync clock and the clock after it, so
// sample_en is masked in those two clocks (one-tick-bit mode excluded).

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
    output wire        sample_en,
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
    wire [8:0] sample_tick = {1'b0, active_tseg1};

    wire one_tick_bit = (active_tseg1 == 8'd0) && (active_tseg2 == 8'd0);

    reg [7:0]  clk_cnt;
    reg [8:0]  tseg_cnt;
    reg [15:0] ssp_shift;
    reg        brs_active_d;
    reg        sample_en_r;
    reg        sync_edge_d;

    wire tick_en      = (clk_cnt == active_prescaler - 8'd1);
    wire phase_change = (brs_active != brs_active_d);

    // Restart the bit sequencer on the sync clock itself (any prescaler
    // phase); in one-tick-bit mode there is nothing to restart.
    wire sync_restart = sync_edge && !one_tick_bit;
    // Mask stale pre-sync sample strobes (sync clock and the clock after).
    wire mask_stale   = (sync_edge || sync_edge_d) && !one_tick_bit;

    assign sample_en = sample_en_r && !mask_stale;

    assign ssp_sample_en = (SSP_OFFSET == 0 || !brs_active)
        ? sample_en
        : ssp_shift[SSP_OFFSET];

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            clk_cnt      <= 8'd0;
            tseg_cnt     <= 9'd0;
            sample_en_r  <= 1'b0;
            bit_boundary <= 1'b0;
            ssp_shift    <= 16'd0;
            brs_active_d <= 1'b0;
            sync_edge_d  <= 1'b0;
        end else begin
            sample_en_r  <= 1'b0;
            bit_boundary <= 1'b0;
            brs_active_d <= brs_active;
            sync_edge_d  <= sync_edge;

            if (phase_change || tick_en) begin
                clk_cnt <= 8'd0;
            end else begin
                clk_cnt <= clk_cnt + 8'd1;
            end

            if (phase_change) begin
                // New phase starts a fresh bit: counters realigned.
                tseg_cnt <= 9'd0;
                if (one_tick_bit) begin
                    sample_en_r  <= 1'b1;
                    bit_boundary <= 1'b1;
                end
            end else if (sync_restart) begin
                // Hard sync on the sync clock itself. Only the bit
                // sequencer restarts: tseg_cnt clears, the prescaler keeps
                // running, so the next tick is simply the first tick of the
                // restarted bit and the bit period stays exact.
                tseg_cnt <= 9'd0;
            end else if (tick_en) begin
                ssp_shift <= {ssp_shift[14:0], sample_en};

                if (one_tick_bit) begin
                    sample_en_r  <= 1'b1;
                    bit_boundary <= 1'b1;
                    tseg_cnt     <= 9'd0;
                end else begin
                    if (tseg_cnt == sample_tick) begin
                        sample_en_r <= 1'b1;
                    end

                    if (tseg_cnt == total_ticks - 9'd1) begin
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
