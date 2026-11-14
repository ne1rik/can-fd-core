`timescale 1ns/1ps

// Loopback with a single-bit XOR fault injector on the bus.
module can_fd_loopback_inject #(
    parameter int EXTENDED = 0,
    parameter int CLASSIC  = 0
)(
    input  wire         clk, rst_n,
    input  wire         tx_start,
    input  wire [28:0]  tx_id,
    input  wire [3:0]   tx_dlc,
    input  wire [511:0] tx_data,
    input  wire         tx_brs,
    input  wire         inject_xor,
    output wire         tx_bit,
    output wire         tx_bit_valid,
    output wire         tx_done,
    output wire         tx_busy,
    output wire [28:0]  rx_id,
    output wire [3:0]   rx_dlc,
    output wire [511:0] rx_data,
    output wire         rx_done,
    output wire         rx_valid,
    output wire         rx_crc_err,
    output wire         rx_stuff_err,
    output wire         rx_ack
);
    wire tx_bit_w, tx_vld_w, tx_done_w, tx_busy_w, rx_ack_w;
    wire bus_clean, bus_faulty;

    can_fd_tx #(.EXTENDED(EXTENDED), .CLASSIC(CLASSIC)) u_tx (
        .clk(clk), .rst_n(rst_n),
        .tx_start(tx_start), .tx_id(tx_id), .tx_dlc(tx_dlc),
        .tx_data(tx_data), .tx_brs(tx_brs),
        .tx_bit(tx_bit_w), .tx_bit_valid(tx_vld_w),
        .tx_done(tx_done_w), .tx_busy(tx_busy_w)
    );

    assign bus_clean  = tx_bit_w & rx_ack_w;
    assign bus_faulty = bus_clean ^ inject_xor;

    can_fd_rx #(.EXTENDED(EXTENDED), .CLASSIC(CLASSIC)) u_rx (
        .clk(clk), .rst_n(rst_n),
        .rx_bit(bus_faulty), .rx_ack(rx_ack_w),
        .rx_id(rx_id), .rx_dlc(rx_dlc), .rx_data(rx_data),
        .rx_done(rx_done), .rx_valid(rx_valid),
        .rx_crc_err(rx_crc_err), .rx_stuff_err(rx_stuff_err)
    );

    assign tx_bit       = bus_faulty;
    assign tx_bit_valid = tx_vld_w;
    assign tx_done      = tx_done_w;
    assign tx_busy      = tx_busy_w;
    assign rx_ack       = rx_ack_w;
endmodule
