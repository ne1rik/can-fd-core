"""Strict single-frame check. Hard asserts - never passes on a broken frame."""
import os
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer
from can_fd_reference import generate_can_fd_frame, dlc_len

EXT = int(os.environ.get("EXTENDED", "0")) == 1
CLS = int(os.environ.get("CLASSIC", "0")) == 1


@cocotb.test()
async def test_timing_debug_strict(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    dut.rst_n.value = 0
    dut.tx_start.value = 0
    dut.tx_data.value = 0
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)

    fid = 0x1127B78 if EXT else 0x16b
    dlc = int(os.environ.get("DBG_DLC", "7"))
    brs = False if CLS else bool(int(os.environ.get("DBG_BRS", "0")))
    n = dlc_len(dlc, classic=CLS)
    data = [(0x11 * (i + 1)) & 0xFF for i in range(n)]

    ref = generate_can_fd_frame(fid, dlc, data, brs, extended=EXT, classic=CLS)
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
    dut.tx_brs.value = int(brs)
    dut.tx_data.value = (int.from_bytes(bytes(data), "big") << (512 - 8 * n)) if n else 0
    dut.tx_start.value = 1
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")
    dut.tx_start.value = 0

    done = False
    for _ in range(len(ref) * 400 + 20000):
        await RisingEdge(dut.clk)
        await Timer(1, unit="ns")
        if int(dut.rx_done.value) == 1:
            done = True
            break
    cap.cancel()

    cocotb.log.info("model len=%d: %s", len(ref), "".join(map(str, ref)))
    cocotb.log.info("bus   len=%d: %s", len(bus), "".join(map(str, bus)))
    cocotb.log.info("RX done=%d crc=%d stuff=%d valid=%d id=%#x dlc=%d",
                    done, int(dut.rx_crc_err.value), int(dut.rx_stuff_err.value),
                    int(dut.rx_valid.value), int(dut.rx_id.value), int(dut.rx_dlc.value))

    assert done, "timeout: rx_done never asserted"
    assert len(bus) == len(ref), f"bus length {len(bus)} != model {len(ref)}"
    ack = len(ref) - 9
    diffs = [i for i in range(len(ref)) if bus[i] != ref[i] and i != ack]
    if diffs:
        i = diffs[0]
        cocotb.log.error("first diff at %d: model=%d bus=%d", i, ref[i], bus[i])
        cocotb.log.error("model: %s", "".join(map(str, ref[max(0,i-8):i+10])))
        cocotb.log.error("bus  : %s", "".join(map(str, bus[max(0,i-8):i+10])))
    assert not diffs, f"{len(diffs)} bit diffs (ACK slot excluded)"
    assert bus[ack] == 0 and ref[ack] == 1, "ACK slot must be dominant on bus"
    assert int(dut.rx_valid.value) == 1, "RX must accept the frame"
    assert int(dut.rx_crc_err.value) == 0, "no CRC error allowed"
    assert int(dut.rx_stuff_err.value) == 0, "no stuff error allowed"
    assert int(dut.rx_id.value) == fid, "ID mismatch"
    assert int(dut.rx_dlc.value) == dlc, "DLC mismatch"
    rx = int(dut.rx_data.value)
    for k in range(n):
        got = (rx >> (512 - 8 * (k + 1))) & 0xFF
        assert got == data[k], f"byte{k}: {got:#04x} != {data[k]:#04x}"
