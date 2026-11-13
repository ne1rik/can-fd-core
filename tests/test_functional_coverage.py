"""Functional coverage tests for CAN FD TX."""

import os
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer

from canfd_kit.coverage import CANFDCoverage, CoverageReport
from can_fd_reference import generate_can_fd_frame, dlc_len, frame_layout


COVERAGE = CANFDCoverage()


async def _reset(dut):
    dut.rst_n.value = 0
    dut.tx_start.value = 0
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)


async def _run_tx(dut, fid, dlc, data, brs):
    n = dlc_len(dlc)
    dut.tx_id.value = fid
    dut.tx_dlc.value = dlc
    dut.tx_brs.value = 1 if brs else 0
    if n:
        dut.tx_data.value = int.from_bytes(bytes(data[:n]), "big") << (512 - 8 * n)
    dut.tx_start.value = 1
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")
    dut.tx_start.value = 0
    for _ in range(5000):
        await RisingEdge(dut.clk)
        if int(dut.tx_done.value) == 1:
            break


def _sample(fid, dlc, data, brs):
    lay = frame_layout(fid, dlc, data, brs)
    COVERAGE.sample_frame(fid, dlc, data[:dlc_len(dlc)], brs, lay["dyn_count"], "none")


PATTERNS = {
    "zeros":       lambda n: [0x00] * n,
    "ones":        lambda n: [0xFF] * n,
    "alternating": lambda n: [0xAA if i % 2 == 0 else 0x55 for i in range(n)],
    "ramp":        lambda n: [i & 0xFF for i in range(n)],
    "random":      lambda n: [(i * 17 + 42) & 0xFF for i in range(n)],
}


@cocotb.test()
async def test_cov_dlc_sweep(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await _reset(dut)
    for dlc in range(16):
        data = PATTERNS["random"](dlc_len(dlc))
        await _run_tx(dut, 0x123, dlc, data, True)
        _sample(0x123, dlc, data, True)
    cocotb.log.info("cov: DLC sweep done")


@cocotb.test()
async def test_cov_brs_both(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await _reset(dut)
    for dlc in range(16):
        for brs in (False, True):
            data = PATTERNS["ramp"](dlc_len(dlc))
            await _run_tx(dut, 0x456, dlc, data, brs)
            _sample(0x456, dlc, data, brs)
    cocotb.log.info("cov: BRS sweep done")


@cocotb.test()
async def test_cov_all_patterns(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await _reset(dut)
    for dlc in range(16):
        for gen in PATTERNS.values():
            data = gen(dlc_len(dlc))
            await _run_tx(dut, 0x123, dlc, data, True)
            _sample(0x123, dlc, data, True)
    cocotb.log.info("cov: pattern sweep done")


@cocotb.test()
async def test_cov_id_ranges(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await _reset(dut)
    ids = [0x000, 0x001, 0x1FF, 0x200, 0x3FF, 0x400, 0x5FF, 0x600, 0x7FF]
    for fid in ids:
        for gen in PATTERNS.values():
            data = gen(dlc_len(8))
            await _run_tx(dut, fid, 8, data, True)
            _sample(fid, 8, data, True)
    cocotb.log.info("cov: ID range sweep done")


@cocotb.test()
async def test_cov_stuff_density(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await _reset(dut)
    cases = [
        (0x000, 8,  [0x00] * 8,  True),
        (0x7FF, 8,  [0xFF] * 8,  True),
        (0x555, 8,  [0x55] * 8,  True),
        (0x2AA, 8,  [0xAA] * 8,  True),
        (0x123, 15, [0x00] * 64, True),
        (0x123, 15, [0xFF] * 64, True),
        (0x123, 9,  [0xAA] * 12, True),
    ]
    for fid, dlc, data, brs in cases:
        await _run_tx(dut, fid, dlc, data, brs)
        _sample(fid, dlc, data, brs)
    cocotb.log.info("cov: stuff density sweep done")


@cocotb.test()
async def test_cov_report(dut):
    """Generate the coverage report and assert minimum target."""
    report = CoverageReport(COVERAGE)
    os.makedirs("coverage", exist_ok=True)
    COVERAGE.save("coverage/db_tx.json")
    report.to_json("coverage/coverage_tx_report.json")
    report.to_file("coverage/coverage_tx.md")

    cocotb.log.info("=" * 60)
    cocotb.log.info("FUNCTIONAL COVERAGE REPORT")
    cocotb.log.info("=" * 60)
    cocotb.log.info("Overall: %.1f%%", report.overall_percentage)
    for g in COVERAGE.groups:
        cocotb.log.info("  %-20s: %3d/%3d bins (%5.1f%%)",
                        g.name, g.covered_bins, g.total_bins, g.percentage)
    for c in COVERAGE.crosses:
        cocotb.log.info("  Cross %-15s: %3d/%3d (%5.1f%%)",
                        c.name, c.covered_bins, c.expected_bins, c.percentage)
    cocotb.log.info("=" * 60)

    # TX-only run cannot hit fault bins; the merged report is the gate.
    for g in (COVERAGE.dlc, COVERAGE.brs, COVERAGE.crc_width,
              COVERAGE.data_pattern, COVERAGE.id_range, COVERAGE.stuff_density):
        assert g.covered_bins == g.total_bins, \
            f"{g.name}: {g.covered_bins}/{g.total_bins}"
    assert COVERAGE.cross_dlc_brs.percentage == 100.0
    assert COVERAGE.cross_id_pattern.percentage == 100.0
