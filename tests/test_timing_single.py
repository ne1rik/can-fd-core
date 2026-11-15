"""Single frame in real timing — does it work?"""
import os
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer
from can_fd_reference import generate_can_fd_frame, dlc_len

EXT = int(os.environ.get("EXTENDED", "0")) == 1
CLS = int(os.environ.get("CLASSIC", "0")) == 1


@cocotb.test()
async def test_timing_single(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    dut.rst_n.value = 0
    dut.tx_start.value = 0
    dut.tx_data.value = 0
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)

    fid = 0x1127B78 if EXT else 0x16b
    dlc = int(os.environ.get("DBG_DLC", "8"))
    brs = False if CLS else bool(int(os.environ.get("DBG_BRS", "0")))
    n = dlc_len(dlc, classic=CLS)
    data = [(0x11 * (i + 1)) & 0xFF for i in range(n)]
    ref = generate_can_fd_frame(fid, dlc, data, brs, extended=EXT, classic=CLS)

    bus = []
    async def cap():
        while True:
            await RisingEdge(dut.clk)
            await Timer(1, unit="ns")
            if int(dut.tx_bit_valid.value) == 1:
                bus.append(int(dut.tx_bit.value))

    c = cocotb.start_soon(cap())
    dut.tx_id.value = fid
    dut.tx_dlc.value = dlc
    dut.tx_brs.value = int(brs)
    dut.tx_data.value = (int.from_bytes(bytes(data), "big") << (512 - 8 * n)) if n else 0
    dut.tx_start.value = 1
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")
    dut.tx_start.value = 0

    done = False
    for _ in range(len(ref) * 70 + 20000):
        await RisingEdge(dut.clk)
        await Timer(1, unit="ns")
        if int(dut.rx_done.value) == 1:
            done = True
            break
    c.cancel()

    cocotb.log.info("bus=%d model=%d done=%d crc=%d stuff=%d valid=%d",
                    len(bus), len(ref), done, int(dut.rx_crc_err.value),
                    int(dut.rx_stuff_err.value), int(dut.rx_valid.value))

    assert done, "timeout"
    assert len(bus) == len(ref), f"len {len(bus)} != {len(ref)}"
    ack = len(ref) - 9
    diffs = [i for i in range(len(ref)) if bus[i] != ref[i] and i != ack]
    assert not diffs, f"{len(diffs)} diffs first={diffs[0]}"
    assert int(dut.rx_valid.value) == 1, "RX rejected"
