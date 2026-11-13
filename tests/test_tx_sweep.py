"""TX core vs reference model: DLC 0..15 x BRS x patterns x IDs."""

import random
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer

from canfd_kit.bus.canfd_bus import CANFDMonitor
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
    mon = CANFDMonitor(dut, "tx_bit", "tx_bit_valid")
    task = cocotb.start_soon(mon.capture_frame(timeout_cycles=40000))

    dut.tx_id.value = fid
    dut.tx_dlc.value = dlc
    dut.tx_brs.value = 1 if brs else 0
    if n:
        dut.tx_data.value = int.from_bytes(bytes(data[:n]), "big") << (512 - 8*n)

    dut.tx_start.value = 1
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")
    dut.tx_start.value = 0

    got = await task
    ref = generate_can_fd_frame(fid, dlc, list(data[:n]), bool(brs))

    tag = f"fid={fid:#05x} dlc={dlc} brs={int(brs)}"
    assert len(got) == len(ref), f"{tag}: len {len(got)} != {len(ref)}"
    if got != ref:
        i = next(k for k, (a, b) in enumerate(zip(got, ref)) if a != b)
        raise AssertionError(f"{tag}: first bit diff at {i}")


PATTERNS = {
    "00": lambda n: [0x00] * n,
    "FF": lambda n: [0xFF] * n,
    "AA": lambda n: [0xAA] * n,
    "55": lambda n: [0x55] * n,
    "ramp": lambda n: [(i * 37 + 11) & 0xFF for i in range(n)],
}


@cocotb.test()
async def test_tx_all_dlc_all_patterns_both_brs(dut):
    """16 DLC x 5 patterns x 2 BRS = 160 frames."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await _reset(dut)
    count = 0
    for dlc in range(16):
        n = dlc_len(dlc)
        for name, gen in PATTERNS.items():
            for brs in (False, True):
                await _case(dut, 0x123, dlc, gen(n), brs)
                count += 1
    cocotb.log.info("TX sweep: %d frames verified", count)


@cocotb.test()
async def test_tx_id_boundaries(dut):
    """IDs that stress stuffing in the arbitration field."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await _reset(dut)
    for fid in (0x000, 0x001, 0x7FF, 0x7FE, 0x555, 0x2AA, 0x100, 0x200, 0x5AA):
        for dlc in (0, 8, 15):
            await _case(dut, fid, dlc, [0xFF] * dlc_len(dlc), True)


@cocotb.test()
async def test_tx_back_to_back(dut):
    """No idle gap between frames; core must return to IDLE cleanly."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await _reset(dut)
    for k in range(12):
        await _case(dut, 0x100 + k, k % 16, [k & 0xFF] * dlc_len(k % 16), k % 2)


@cocotb.test()
async def test_tx_reset_midframe(dut):
    """Reset during shift-out must abort, and the next frame must be clean."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await _reset(dut)

    dut.tx_id.value = 0x123
    dut.tx_dlc.value = 15
    dut.tx_brs.value = 1
    dut.tx_data.value = int.from_bytes(bytes([0xAA] * 64), "big")
    dut.tx_start.value = 1
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")
    dut.tx_start.value = 0

    for _ in range(200):
        await RisingEdge(dut.clk)
    await _reset(dut)
    assert int(dut.tx_bit_valid.value) == 0, "valid must be low after reset"

    await _case(dut, 0x5AA, 8, [0xFF] * 8, True)


@cocotb.test()
async def test_tx_randomised(dut):
    """Seeded random regression, reproducible."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await _reset(dut)
    rng = random.Random(0xC0FFEE)
    for _ in range(60):
        dlc = rng.randrange(16)
        n = dlc_len(dlc)
        await _case(dut, rng.randrange(0x800), dlc,
                    [rng.randrange(256) for _ in range(n)],
                    bool(rng.randrange(2)))
