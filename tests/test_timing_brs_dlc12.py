import os
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer
from can_fd_reference import generate_can_fd_frame, dlc_len

@cocotb.test()
async def test_brs_dlc12(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    dut.rst_n.value = 0
    dut.tx_start.value = 0
    dut.tx_data.value = 0
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)

    fid = 0x234
    dlc = 12
    n = dlc_len(dlc, classic=False)
    data = [i & 0xFF for i in range(n)]
    ref = generate_can_fd_frame(fid, dlc, data, True, extended=False, classic=False)
    
    bus = []
    async def capture():
        while True:
            await RisingEdge(dut.clk)
            await Timer(1, unit="ns")
            if int(dut.tx_bit_valid.value) == 1:
                bus.append(int(dut.tx_bit.value))
    cap = cocotb.start_soon(capture())
    
    dut.tx_id.value = fid
    dut.tx_dlc.value = dlc
    dut.tx_brs.value = 1
    dut.tx_data.value = int.from_bytes(bytes(data), "big") << (512 - 8 * n)
    dut.tx_start.value = 1
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")
    dut.tx_start.value = 0
    
    done = False
    for _ in range(len(ref) * 17 * 4 + 40000):
        await RisingEdge(dut.clk)
        await Timer(1, unit="ns")
        if int(dut.rx_done.value) == 1:
            done = True
            break
    cap.cancel()
    
    cocotb.log.info("bus=%d model=%d rx_done=%d crc=%d stuff=%d valid=%d",
                    len(bus), len(ref), done, int(dut.rx_crc_err.value),
                    int(dut.rx_stuff_err.value), int(dut.rx_valid.value))
    
    assert done, "timeout"
    assert len(bus) == len(ref), f"len {len(bus)} != {len(ref)}"
    assert int(dut.rx_valid.value) == 1, "RX rejected"
