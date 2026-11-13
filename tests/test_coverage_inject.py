"""Fault-injection coverage with varied dimensions.

Two sweeps:
  * fault x DLC            (error_x_dlc)   — payload fixed to zeros/ID 0x000
  * fault x data_pattern   (fault_x_pattern) — pattern and ID varied per fault

stuff_flip uses ID 0x000 so the header always contains long zero runs and a
dynamic stuff bit exists for every payload pattern. payload_flip needs DLC>0.
"""

import os
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer

from canfd_kit.coverage import CANFDCoverage, CoverageReport
from can_fd_reference import frame_layout, dlc_len


COVERAGE = CANFDCoverage()
FAULTS = ("none", "payload_flip", "crc_flip", "stuff_flip", "sc_flip")

PATTERNS = {
    "zeros":       lambda n: [0x00] * n,
    "ones":        lambda n: [0xFF] * n,
    "alternating": lambda n: [0xAA if i % 2 == 0 else 0x55 for i in range(n)],
    "ramp":        lambda n: [i & 0xFF for i in range(n)],
    "random":      lambda n: [(i * 17 + 42) & 0xFF for i in range(n)],
}


async def _reset(dut):
    dut.rst_n.value = 0
    dut.tx_start.value = 0
    dut.inject_xor.value = 0
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)


async def _injector(dut, target):
    idx = -1
    while True:
        await RisingEdge(dut.clk)
        await Timer(1, unit="ns")
        dut.inject_xor.value = 0
        if int(dut.tx_bit_valid.value) == 1:
            idx += 1
            if target is not None and idx == target:
                dut.inject_xor.value = 1


def _target(lay, fault):
    if fault == "none":
        return None
    if fault == "payload_flip":
        return lay["stuffed_data_len"] - 1     # always the last payload bit
    if fault == "crc_flip":
        return lay["crc_bit_indices"][len(lay["crc_bit_indices"]) // 2]
    if fault == "sc_flip":
        return lay["sc_indices"][0]
    if fault == "stuff_flip":
        return lay["dyn_stuff_indices"][-1]
    raise ValueError(fault)


async def _case(dut, fid, dlc, data, brs, fault):
    n = dlc_len(dlc)
    lay = frame_layout(fid, dlc, data, brs)
    tgt = _target(lay, fault)

    inj = cocotb.start_soon(_injector(dut, tgt))

    dut.tx_id.value = fid
    dut.tx_dlc.value = dlc
    dut.tx_brs.value = 1 if brs else 0
    if n:
        dut.tx_data.value = int.from_bytes(bytes(data[:n]), "big") << (512 - 8 * n)

    dut.tx_start.value = 1
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")
    dut.tx_start.value = 0

    done = False
    for _ in range(len(lay["bits"]) * 3 + 3000):
        await RisingEdge(dut.clk)
        await Timer(1, unit="ns")
        if int(dut.rx_done.value) == 1:
            done = True
            break

    valid = int(dut.rx_valid.value)
    inj.cancel()
    dut.inject_xor.value = 0
    for _ in range(5):
        await RisingEdge(dut.clk)

    COVERAGE.sample_frame(fid, dlc, data[:n], brs, lay["dyn_count"], fault)

    tag = f"id={fid:#05x} dlc={dlc} brs={int(brs)} fault={fault}"
    assert done, f"{tag}: rx_done never asserted"
    if fault == "none":
        assert valid == 1, f"{tag}: clean frame rejected"
    else:
        assert valid == 0, f"{tag}: fault went UNDETECTED"


@cocotb.test()
async def test_cov_fault_dlc_sweep(dut):
    """error_x_dlc: 16 DLC x faults x BRS, payload zeros / ID 0x000."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await _reset(dut)
    count = 0
    for dlc in range(16):
        data = [0x00] * dlc_len(dlc)
        for fault in FAULTS:
            if fault == "payload_flip" and dlc == 0:
                continue
            for brs in (False, True):
                await _case(dut, 0x000, dlc, data, brs, fault)
                count += 1
    cocotb.log.info("fault x dlc sweep: %d frames", count)


@cocotb.test()
async def test_cov_fault_pattern_sweep(dut):
    """fault_x_pattern: vary payload pattern and ID for every fault type."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await _reset(dut)
    count = 0
    for pname, gen in PATTERNS.items():
        for fault in FAULTS:
            if fault == "stuff_flip":
                fid, dlc = 0x000, 8       # header zero-runs guarantee stuff bits
            elif fault == "payload_flip":
                fid, dlc = 0x123, 8       # needs a payload
            else:
                fid, dlc = 0x123, 8
            data = gen(dlc_len(dlc))
            for brs in (False, True):
                await _case(dut, fid, dlc, data, brs, fault)
                count += 1
    cocotb.log.info("fault x pattern sweep: %d frames", count)


@cocotb.test()
async def test_cov_inject_report(dut):
    report = CoverageReport(COVERAGE)
    os.makedirs("coverage", exist_ok=True)
    COVERAGE.save("coverage/db_inject.json")
    report.to_json("coverage/coverage_inject_report.json")
    report.to_file("coverage/coverage_inject.md")

    cocotb.log.info("inject run: points %.1f%%, crosses %.1f%%, overall %.1f%%",
                    report.point_percentage, report.cross_percentage,
                    report.overall_percentage)
    for x in COVERAGE.crosses:
        cocotb.log.info("  cross %-16s %3d/%3d", x.name, x.covered_bins, x.expected_bins)

    assert COVERAGE.error_type.covered_bins == COVERAGE.error_type.total_bins
    assert COVERAGE.cross_error_dlc.percentage == 100.0
    assert COVERAGE.cross_fault_pattern.percentage == 100.0, \
        f"fault_x_pattern {COVERAGE.cross_fault_pattern.covered_bins}/{COVERAGE.cross_fault_pattern.expected_bins}"
    assert COVERAGE.cross_error_dlc.illegal_hits == 0
