"""Fault-injection coverage sweep: every DLC x every fault type x both BRS.

ID=0x000 with an all-zero payload guarantees long runs, so a dynamic stuff bit
always exists and stuff_flip is reachable for every DLC including 0.
payload_flip is skipped for DLC=0 (no payload) and declared illegal in the model.
"""

import os
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer

from canfd_kit.coverage import CANFDCoverage, CoverageReport
from can_fd_reference import frame_layout, dlc_len


COVERAGE = CANFDCoverage()
FAULTS = ("none", "payload_flip", "crc_flip", "stuff_flip", "sc_flip")


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


def _target(lay, fault, n):
    if fault == "none":
        return None
    if fault == "payload_flip":
        # Last bit of the stuffed data region is always the final payload bit,
        # never a stuff bit (a boundary stuff bit is moved into the CRC field).
        return lay["stuffed_data_len"] - 1
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
    tgt = _target(lay, fault, n)

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

    tag = f"dlc={dlc} brs={int(brs)} fault={fault}"
    assert done, f"{tag}: rx_done never asserted"
    if fault == "none":
        assert valid == 1, f"{tag}: clean frame rejected"
    else:
        assert valid == 0, f"{tag}: fault went UNDETECTED"


@cocotb.test()
async def test_cov_fault_sweep(dut):
    """16 DLC x 5 faults x 2 BRS, minus the impossible payload_flip@DLC0."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await _reset(dut)
    fid = 0x000
    count = 0
    for dlc in range(16):
        data = [0x00] * dlc_len(dlc)
        for fault in FAULTS:
            if fault == "payload_flip" and dlc == 0:
                continue
            for brs in (False, True):
                await _case(dut, fid, dlc, data, brs, fault)
                count += 1
    cocotb.log.info("fault sweep: %d frames, all faults detected", count)


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
    for g in COVERAGE.groups:
        cocotb.log.info("  %-16s %3d/%3d", g.name, g.covered_bins, g.total_bins)
    for x in COVERAGE.crosses:
        cocotb.log.info("  cross %-14s %3d/%3d (illegal hits %d)",
                        x.name, x.covered_bins, x.expected_bins, x.illegal_hits)

    assert COVERAGE.error_type.covered_bins == COVERAGE.error_type.total_bins
    assert COVERAGE.cross_error_dlc.percentage == 100.0, \
        f"error_x_dlc {COVERAGE.cross_error_dlc.covered_bins}/{COVERAGE.cross_error_dlc.expected_bins}"
    assert COVERAGE.cross_error_dlc.illegal_hits == 0, "sampled an impossible cell"
