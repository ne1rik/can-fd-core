"""RX via loopback: DLC 0..15 x BRS x patterns, plus randomised traffic."""

import random
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer

from can_fd_reference import generate_can_fd_frame, dlc_len


async def _reset(dut):
    dut.rst_n.value = 0
    dut.tx_start.value = 0
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)


async def _case(dut, fid, dlc, data, brs):
    n = dlc_len(dlc)
    ref_len = len(generate_can_fd_frame(fid, dlc, list(data[:n]), bool(brs)))

    dut.tx_id.value = fid
    dut.tx_dlc.value = dlc
    dut.tx_brs.value = 1 if brs else 0
    if n:
        dut.tx_data.value = int.from_bytes(bytes(data[:n]), "big") << (512 - 8*n)

    dut.tx_start.value = 1
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")
    dut.tx_start.value = 0

    done = False
    for _ in range(ref_len * 3 + 3000):
        await RisingEdge(dut.clk)
        await Timer(1, unit="ns")
        if int(dut.rx_done.value) == 1:
            done = True
            break

    tag = f"fid={fid:#05x} dlc={dlc} brs={int(brs)}"
    assert done, f"{tag}: rx_done never asserted"
    assert int(dut.rx_crc_err.value) == 0, f"{tag}: crc_err set"
    assert int(dut.rx_stuff_err.value) == 0, f"{tag}: stuff_err set"
    assert int(dut.rx_valid.value) == 1, f"{tag}: rx_valid low"
    assert int(dut.rx_id.value) == fid, f"{tag}: id {int(dut.rx_id.value):#x}"
    assert int(dut.rx_dlc.value) == dlc, f"{tag}: dlc {int(dut.rx_dlc.value)}"

    rx = int(dut.rx_data.value)
    for i in range(n):
        got = (rx >> (512 - 8*(i+1))) & 0xFF
        assert got == data[i], f"{tag}: byte {i} {got:#04x} != {data[i]:#04x}"


PATTERNS = {
    "00": lambda n: [0x00] * n,
    "FF": lambda n: [0xFF] * n,
    "AA": lambda n: [0xAA] * n,
    "55": lambda n: [0x55] * n,
    "ramp": lambda n: [(i * 37 + 11) & 0xFF for i in range(n)],
}


@cocotb.test()
async def test_loopback_all_dlc_all_patterns_both_brs(dut):
    """160 frames through TX -> wire -> RX."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await _reset(dut)
    count = 0
    for dlc in range(16):
        n = dlc_len(dlc)
        for _name, gen in PATTERNS.items():
            for brs in (False, True):
                await _case(dut, 0x123, dlc, gen(n), brs)
                count += 1
    cocotb.log.info("loopback sweep: %d frames verified", count)


@cocotb.test()
async def test_loopback_id_boundaries(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await _reset(dut)
    for fid in (0x000, 0x001, 0x7FF, 0x7FE, 0x555, 0x2AA, 0x100, 0x200):
        for dlc in (0, 1, 8, 11, 15):
            await _case(dut, fid, dlc, [0xFF] * dlc_len(dlc), True)


@cocotb.test()
async def test_loopback_crc21_threshold(dut):
    """DLC 10 -> 16 bytes -> CRC-17; DLC 11 -> 20 bytes -> CRC-21."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await _reset(dut)
    for dlc in (10, 11, 12, 13):
        for pattern in (0x00, 0xFF, 0xA5):
            await _case(dut, 0x321, dlc, [pattern] * dlc_len(dlc), True)


@cocotb.test()
async def test_loopback_randomised(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await _reset(dut)
    rng = random.Random(0xBADF00D)
    for _ in range(50):
        dlc = rng.randrange(16)
        n = dlc_len(dlc)
        await _case(dut, rng.randrange(0x800), dlc,
                    [rng.randrange(256) for _ in range(n)],
                    bool(rng.randrange(2)))
