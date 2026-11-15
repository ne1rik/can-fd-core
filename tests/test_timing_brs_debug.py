"""Diagnostic: where does BRS phase switching fail?"""
import os
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer
from can_fd_reference import generate_can_fd_frame, frame_layout, dlc_len

EXT = int(os.environ.get("EXTENDED", "0")) == 1
CLS = int(os.environ.get("CLASSIC", "0")) == 1


@cocotb.test()
async def test_brs_diagnostic(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    dut.rst_n.value = 0
    dut.tx_start.value = 0
    dut.tx_data.value = 0
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)

    fid = 0x16b
    dlc = 8
    brs = True
    n = dlc_len(dlc, classic=CLS)
    data = [0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88][:n]
    
    ref = generate_can_fd_frame(fid, dlc, data, brs, extended=EXT, classic=CLS)
    layout = frame_layout(fid, dlc, data, brs, extended=EXT, classic=CLS)
    
    brs_raw_idx = layout["brs_index"]
    brs_stuffed_idx = layout.get("brs_stuffed_index", "N/A")
    
    cocotb.log.info("BRS raw index: %d", brs_raw_idx)
    cocotb.log.info("BRS stuffed index: %s", brs_stuffed_idx)
    cocotb.log.info("Model len: %d", len(ref))
    cocotb.log.info("Model: %s", "".join(map(str, ref)))
    
    bus = []
    tx_phase_changes = []
    rx_phase_changes = []
    
    async def monitor():
        tx_phase_prev = 0
        rx_phase_prev = 0
        while True:
            await RisingEdge(dut.clk)
            await Timer(1, unit="ns")
            if int(dut.tx_bit_valid.value) == 1:
                bus.append(int(dut.tx_bit.value))
            
            # Monitor TX phase
            try:
                tx_phase = int(dut.u_tx.br_phase.value)
                if tx_phase != tx_phase_prev:
                    tx_phase_changes.append((len(bus), tx_phase))
                    tx_phase_prev = tx_phase
            except:
                pass
            
            # Monitor RX phase
            try:
                rx_phase = int(dut.u_rx.bt_phase.value)
                if rx_phase != rx_phase_prev:
                    rx_phase_changes.append((len(bus), rx_phase))
                    rx_phase_prev = rx_phase
            except:
                pass
    
    mon = cocotb.start_soon(monitor())
    
    dut.tx_id.value = fid
    dut.tx_dlc.value = dlc
    dut.tx_brs.value = int(brs)
    dut.tx_data.value = (int.from_bytes(bytes(data), "big") << (512 - 8 * n)) if n else 0
    dut.tx_start.value = 1
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")
    dut.tx_start.value = 0
    
    budget = len(ref) * 17 * 4 + 40000
    done = False
    for _ in range(budget):
        await RisingEdge(dut.clk)
        await Timer(1, unit="ns")
        if int(dut.rx_done.value) == 1:
            done = True
            break
    mon.cancel()
    
    cocotb.log.info("Bus len: %d, RX done: %d", len(bus), done)
    cocotb.log.info("TX phase changes: %s", tx_phase_changes)
    cocotb.log.info("RX phase changes: %s", rx_phase_changes)
    cocotb.log.info("RX crc=%d stuff=%d valid=%d",
                    int(dut.rx_crc_err.value), int(dut.rx_stuff_err.value),
                    int(dut.rx_valid.value))
    
    if tx_phase_changes and rx_phase_changes:
        tx_switch_bit = tx_phase_changes[0][0]
        rx_switch_bit = rx_phase_changes[0][0]
        cocotb.log.info("TX switches at bit %d, RX switches at bit %d",
                        tx_switch_bit, rx_switch_bit)
        cocotb.log.info("Desync: %d bits", rx_switch_bit - tx_switch_bit)
    
    if bus:
        cocotb.log.info("Bus: %s", "".join(map(str, bus[:100])))
