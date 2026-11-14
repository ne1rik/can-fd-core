`timescale 1ns/1ps
// Fault confinement per ISO 11898-1:2015 section 8.3.
//
// TEC counts up by 8 on every transmit-side error event and down by 1 on a
// successful transmission (tx_done while tx_active). REC counts up by 1 on
// every receive-side error event and down by 1 on a successfully received
// frame (rx_valid). Node state machine:
//   ERROR_ACTIVE  : TEC < 128 and REC < 128
//   ERROR_PASSIVE : TEC >= 128 or REC >= 128 (but not bus-off)
//   BUS_OFF       : TEC >= 256
// Bus-off recovery: 128 x 11 recessive bits on the bus, observed as
// RECOVERY_IDLE_CYCLES consecutive bus_idle cycles. Recovery resets both
// counters and pulses `recovered` for one clock.
//
// Error flag generation: an active node drives the 6-bit dominant active
// error flag; a passive node drives the 6-bit recessive passive flag. Both
// are followed by the recessive error delimiter and IFS (handled by the
// link layer, not by this module).
//
// Note on the "TEC unchanged for passive error flag" ISO rule: this module
// counts +8 on every tx_error pulse because the pin interface carries no
// information about which flag variant the link layer actually sent. The
// flag variant itself is exported via error_flag_active/error_flag_passive.
module can_fault_manager (
    input  wire         clk, rst_n,
    input  wire         tx_error,      // TX detected error (crc/stuff/form)
    input  wire         tx_done,       // TX completed successfully
    input  wire         tx_active,     // TX is transmitting
    input  wire         rx_error,      // RX detected error
    input  wire         rx_valid,      // RX received valid frame
    input  wire         bus_idle,      // bus is recessive (for recovery counting)

    output wire [7:0]   tec,           // Transmit Error Counter
    output wire [7:0]   rec,           // Receive Error Counter
    output wire [1:0]   state,         // 0=ACTIVE, 1=PASSIVE, 2=BUS_OFF
    output wire         error_flag_active,  // generate active error flag
    output wire         error_flag_passive, // generate passive error flag
    output wire         bus_off,            // node is bus-off
    output wire         recovered           // just recovered from bus-off
);

    localparam [1:0] STATE_ACTIVE  = 2'd0;
    localparam [1:0] STATE_PASSIVE = 2'd1;
    localparam [1:0] STATE_BUSOFF  = 2'd2;

    // 128 occurrences of 11 recessive bits = 1408 consecutive idle cycles.
    localparam [11:0] RECOVERY_IDLE_CYCLES = 12'd1408;

    reg [1:0]  state_q;
    reg [8:0]  tec_q;      // 9 bits: needs to hold 256 (bus-off threshold)
    reg [7:0]  rec_q;      // saturates at 255
    reg [11:0] recov_q;    // consecutive idle cycles while bus-off
    reg        recovered_q;

    wire error_event = tx_error || rx_error;

    // Successful transmission: completion signalled while actually
    // transmitting and no error event in the same cycle.
    wire tx_countable = tx_done && tx_active && !tx_error && !rx_error;

    // Next counter values (saturating arithmetic, no wrap-around).
    wire [8:0] tec_after_inc = (tec_q >= 9'd248) ? 9'd256 : (tec_q + 9'd8);
    wire [8:0] tec_after_dec = (tec_q == 9'd0)   ? 9'd0   : (tec_q - 9'd1);
    wire [8:0] tec_nxt = tx_error    ? tec_after_inc :
                         tx_countable ? tec_after_dec : tec_q;

    wire [7:0] rec_after_inc = (rec_q == 8'd255) ? 8'd255 : (rec_q + 8'd1);
    wire [7:0] rec_after_dec = (rec_q == 8'd0)   ? 8'd0   : (rec_q - 8'd1);
    wire [7:0] rec_nxt = rx_error ? rec_after_inc :
                         rx_valid ? rec_after_dec : rec_q;

    wire [1:0] state_nxt = (tec_nxt >= 9'd256)                              ? STATE_BUSOFF  :
                           ((tec_nxt >= 9'd128) || (rec_nxt >= 8'd128))    ? STATE_PASSIVE :
                           STATE_ACTIVE;

    assign bus_off = (state_q == STATE_BUSOFF);
    assign tec = bus_off ? 8'd255 : tec_q[7:0];
    assign rec = rec_q;
    assign state = state_q;

    assign error_flag_active  = (state_q == STATE_ACTIVE)  && error_event;
    assign error_flag_passive = (state_q == STATE_PASSIVE) && error_event;

    assign recovered = recovered_q;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state_q     <= STATE_ACTIVE;
            tec_q       <= 9'd0;
            rec_q       <= 8'd0;
            recov_q     <= 12'd0;
            recovered_q <= 1'b0;
        end else begin
            recovered_q <= 1'b0;
            if (state_q == STATE_BUSOFF) begin
                // Node is disconnected: counters are frozen, only the
                // bus-off recovery sequence is observed.
                if (bus_idle) begin
                    if (recov_q >= RECOVERY_IDLE_CYCLES) begin
                        state_q     <= STATE_ACTIVE;
                        tec_q       <= 9'd0;
                        rec_q       <= 8'd0;
                        recov_q     <= 12'd0;
                        recovered_q <= 1'b1;
                    end else begin
                        recov_q <= recov_q + 12'd1;
                    end
                end else begin
                    // Bus activity restarts the recovery sequence.
                    recov_q <= 12'd0;
                end
            end else begin
                tec_q   <= tec_nxt;
                rec_q   <= rec_nxt;
                state_q <= state_nxt;
            end
        end
    end
endmodule
