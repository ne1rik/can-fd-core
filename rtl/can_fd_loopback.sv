`timescale 1ns/1ps

// Loopback wrapper: connects TX and RX through a wire
module can_fd_loopback (
    input  wire         clk, rst_n,
    
    // TX interface
    input  wire         tx_start,
    input  wire [10:0]  tx_id,
    input  wire [3:0]   tx_dlc,
    input  wire [511:0] tx_data,
    input  wire         tx_brs,
    output wire         tx_bit,
    output wire         tx_bit_valid,
    output wire         tx_done,
    output wire         tx_busy,
    
    // RX interface
    output wire         rx_ack,
    output wire [10:0]  rx_id,
    output wire [3:0]   rx_dlc,
    output wire [511:0] rx_data,
    output wire         rx_done,
    output wire         rx_valid,
    output wire         rx_crc_err,
    output wire         rx_stuff_err
);

    wire bus_wire;
    
    // TX module
    can_fd_tx tx_inst (
        .clk(clk),
        .rst_n(rst_n),
        .tx_start(tx_start),
        .tx_id(tx_id),
        .tx_dlc(tx_dlc),
        .tx_data(tx_data),
        .tx_brs(tx_brs),
        .tx_bit(bus_wire),
        .tx_bit_valid(tx_bit_valid),
        .tx_done(tx_done),
        .tx_busy(tx_busy)
    );
    
    // RX module
    can_fd_rx rx_inst (
        .clk(clk),
        .rst_n(rst_n),
        .rx_bit(bus_wire),
        .rx_ack(rx_ack),
        .rx_id(rx_id),
        .rx_dlc(rx_dlc),
        .rx_data(rx_data),
        .rx_done(rx_done),
        .rx_valid(rx_valid),
        .rx_crc_err(rx_crc_err),
        .rx_stuff_err(rx_stuff_err)
    );
    
    assign tx_bit = bus_wire;

endmodule
