"""Diagnostic: why doesn't TX switch phase?"""
import os
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer
from can_fd_reference import generate_can_fd_frame, dlc_len

EXT = int(os.environ.get("EXTENDED", "0")) == 1
CLS = int(os.environ.get("CLASSIC", "0")) == 1


@cocotb.test()
async def test_brs_tx_diagnostic(dut):
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
    
    bus = []
    brs_transmitted_seen = False
    brs_active_reg_seen = False
    brs_wr_idx_val = None
    rd_idx_when_brs = None
    
    async def monitor():
        nonlocal brs_transmitted_seen, brs_active_reg_seen, brs_wr_idx_val, rd_idx_when_brs
        while True:
            await RisingEdge(dut.clk)
            await Timer(1, unit="ns")
            if int(dut.tx_bit_valid.value) == 1:
                bus.append(int(dut.tx_bit.value))
            
            # Monitor TX internals
            try:
                if not brs_transmitted_seen and int(dut.u_tx.brs_transmitted.value) == 1:
                    brs_transmitted_seen = True
                    cocotb.log.info("brs_transmitted set at bus bit %d", len(bus))
                    brs_wr_idx_val = int(dut.u_tx.brs_wr_idx.value)
                    cocotb.log.info("brs_wr_idx = %d", brs_wr_idx_val)
                
                if not brs_active_reg_seen and int(dut.u_tx.brs_active_reg.value) == 1:
                    brs_active_reg_seen = True
                    cocotb.log.info("brs_active_reg set at bus bit %d", len(bus))
                    rd_idx_when_brs = int(dut.u_tx.rd_idx.value)
                    cocotb.log.info("rd_idx when brs_active_reg set = %d", rd_idx_when_brs)
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
    cocotb.log.info("brs_transmitted seen: %s", brs_transmitted_seen)
    cocotb.log.info("brs_active_reg seen: %s", brs_active_reg_seen)
    cocotb.log.info("brs_wr_idx: %s", brs_wr_idx_val)
    cocotb.log.info("rd_idx when brs_active_reg set: %s", rd_idx_when_brs)
    
    if brs_wr_idx_val is not None and rd_idx_when_brs is not None:
        cocotb.log.info("Mismatch: brs_wr_idx=%d, rd_idx=%d, diff=%d",
                        brs_wr_idx_val, rd_idx_when_brs, rd_idx_when_brs - brs_wr_idx_val)
