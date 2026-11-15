"""Detailed diagnostic: trace brs_wr_idx and rd_idx in F_SHIFT"""
import os
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer
from can_fd_reference import generate_can_fd_frame, dlc_len

@cocotb.test()
async def test_brs_detailed(dut):
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
    n = dlc_len(dlc, classic=False)
    data = [0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88][:n]
    
    ref = generate_can_fd_frame(fid, dlc, data, brs, extended=False, classic=False)
    
    bus = []
    brs_reg_val = None
    brs_wr_idx_val = None
    f_shift_entries = []
    phase_switch_attempt = False
    
    async def monitor():
        nonlocal brs_reg_val, brs_wr_idx_val, phase_switch_attempt
        prev_state = -1
        while True:
            await RisingEdge(dut.clk)
            await Timer(1, unit="ns")
            if int(dut.tx_bit_valid.value) == 1:
                bus.append(int(dut.tx_bit.value))
            
            state = int(dut.u_tx.state.value)
            
            # Track state transitions
            if state != prev_state:
                if state == 1:  # F_RAW
                    brs_reg_val = int(dut.u_tx.brs_reg.value)
                    cocotb.log.info("Enter F_RAW: brs_reg=%d", brs_reg_val)
                elif state == 7:  # F_SHIFT
                    brs_wr_idx_val = int(dut.u_tx.brs_wr_idx.value)
                    cocotb.log.info("Enter F_SHIFT: brs_wr_idx=%d, brs_reg=%d", 
                                    brs_wr_idx_val, int(dut.u_tx.brs_reg.value))
                prev_state = state
            
            # Track F_SHIFT activity
            if state == 7:  # F_SHIFT
                rd_idx = int(dut.u_tx.rd_idx.value)
                wr_len = int(dut.u_tx.wr_len.value)
                brs_active = int(dut.u_tx.brs_active_reg.value)
                f_shift_entries.append((rd_idx, wr_len, brs_wr_idx_val, brs_active))
                
                if rd_idx == brs_wr_idx_val and not phase_switch_attempt:
                    phase_switch_attempt = True
                    cocotb.log.info("rd_idx == brs_wr_idx at bus bit %d: rd_idx=%d, brs_wr_idx=%d, brs_reg=%d, brs_active=%d",
                                    len(bus), rd_idx, brs_wr_idx_val, int(dut.u_tx.brs_reg.value), brs_active)
    
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
    cocotb.log.info("F_SHIFT entries: %d", len(f_shift_entries))
    if f_shift_entries:
        cocotb.log.info("First 5 F_SHIFT: %s", f_shift_entries[:5])
        cocotb.log.info("Last 5 F_SHIFT: %s", f_shift_entries[-5:])
        cocotb.log.info("rd_idx range: %d to %d", 
                        min(e[0] for e in f_shift_entries),
                        max(e[0] for e in f_shift_entries))
        cocotb.log.info("brs_wr_idx was: %s", brs_wr_idx_val)
