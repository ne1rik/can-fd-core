"""Fault injection on the TX -> RX path.

Scope: the current RX only DETECTS faults (crc_err / stuff_err / form_err and
rx_valid low). It does not abort the frame, send an error frame, or maintain
TEC/REC. These tests therefore assert detection only. Two documented gaps are
marked xfail rather than hidden.
"""

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer

from can_fd_reference import frame_layout, dlc_len


async def _reset(dut):
    dut.rst_n.value = 0
    dut.tx_start.value = 0
    dut.inject_xor.value = 0
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)


async def _injector(dut, target):
    """Flip the bit with frame index `target` as the receiver samples it.

    tx_bit holds frame[i] right after edge E_i; the receiver samples it at
    E_{i+1}. We therefore raise inject_xor in the cycle that starts at E_i.
    """
    idx = -1
    while True:
        await RisingEdge(dut.clk)
        await Timer(1, unit="ns")
        dut.inject_xor.value = 0
        if int(dut.tx_bit_valid.value) == 1:
            idx += 1
            if target is not None and idx == target:
                dut.inject_xor.value = 1


async def _run(dut, fid, dlc, data, brs, target):
    lay = frame_layout(fid, dlc, data, brs)
    n = dlc_len(dlc)

    inj = cocotb.start_soon(_injector(dut, target))

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
    for _ in range(len(lay["bits"]) * 3 + 3000):
        await RisingEdge(dut.clk)
        await Timer(1, unit="ns")
        if int(dut.rx_done.value) == 1:
            done = True
            break

    inj.kill()
    dut.inject_xor.value = 0
    await RisingEdge(dut.clk)

    return {
        "done": done,
        "valid": int(dut.rx_valid.value),
        "crc_err": int(dut.rx_crc_err.value),
        "stuff_err": int(dut.rx_stuff_err.value),
        "id": int(dut.rx_id.value),
        "dlc": int(dut.rx_dlc.value),
        "layout": lay,
    }


@cocotb.test()
async def test_injector_is_neutral_without_fault(dut):
    """Control: plumbing alone must not disturb a good frame."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await _reset(dut)
    r = await _run(dut, 0x123, 9, [0xAA] * 12, True, None)
    assert r["done"] and r["valid"] == 1, r
    assert r["id"] == 0x123 and r["dlc"] == 9, r


@cocotb.test()
async def test_flip_payload_bit_is_detected(dut):
    """A flipped data bit must break the CRC."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await _reset(dut)
    fid, dlc, data = 0x123, 9, [0xAA] * 12
    lay = frame_layout(fid, dlc, data, True)
    stuff = set(lay["dyn_stuff_indices"])
    # a payload bit, well inside the data field, not a stuff bit
    target = next(i for i in range(30, lay["stuffed_data_len"])
                  if i not in stuff)
    r = await _run(dut, fid, dlc, data, True, target)
    assert r["done"], "receiver should still complete the frame"
    assert r["valid"] == 0, f"payload flip at {target} went undetected: {r}"
    assert r["crc_err"] == 1, f"expected crc_err, got {r}"


@cocotb.test()
async def test_flip_crc_bit_is_detected(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await _reset(dut)
    fid, dlc, data = 0x123, 9, [0xAA] * 12
    lay = frame_layout(fid, dlc, data, True)
    target = lay["crc_bit_indices"][len(lay["crc_bit_indices"]) // 2]
    r = await _run(dut, fid, dlc, data, True, target)
    assert r["done"]
    assert r["valid"] == 0 and r["crc_err"] == 1, r


@cocotb.test()
async def test_flip_stuff_count_bit_is_detected(dut):
    """SC bits are part of the CRC input, so flipping one must break the CRC."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await _reset(dut)
    fid, dlc, data = 0x123, 9, [0xAA] * 12
    lay = frame_layout(fid, dlc, data, True)
    target = lay["sc_indices"][1]
    r = await _run(dut, fid, dlc, data, True, target)
    assert r["done"]
    assert r["valid"] == 0 and r["crc_err"] == 1, r


@cocotb.test()
async def test_flip_dynamic_stuff_bit_is_detected(dut):
    """Wrong stuff polarity must raise stuff_err (or at least invalidate)."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await _reset(dut)
    fid, dlc, data = 0x000, 8, [0xFF] * 8
    lay = frame_layout(fid, dlc, data, True)
    assert lay["dyn_stuff_indices"], "vector must contain dynamic stuff bits"
    target = lay["dyn_stuff_indices"][-1]
    r = await _run(dut, fid, dlc, data, True, target)
    assert r["done"]
    assert r["valid"] == 0, f"stuff flip at {target} undetected: {r}"


@cocotb.test()
async def test_flip_crc21_bit_is_detected(dut):
    """Same fault on the 21-bit CRC path (DLC >= 11)."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await _reset(dut)
    fid, dlc, data = 0x7FF, 15, [0x5A] * 64
    lay = frame_layout(fid, dlc, data, True)
    assert lay["crc_width"] == 21
    target = lay["crc_bit_indices"][3]
    r = await _run(dut, fid, dlc, data, True, target)
    assert r["done"]
    assert r["valid"] == 0 and r["crc_err"] == 1, r


@cocotb.test(expect_fail=True)
async def test_gap_fixed_stuff_bit_polarity_not_checked(dut):
    """KNOWN GAP: RX ignores fixed stuff bits in the CRC field entirely.

    ISO requires their polarity to alternate. Flipping one is currently
    invisible. This test is expected to fail until that check exists.
    """
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await _reset(dut)
    fid, dlc, data = 0x123, 9, [0xAA] * 12
    lay = frame_layout(fid, dlc, data, True)
    target = lay["fsb_indices"][1]          # a separator FSB, not the leading one
    r = await _run(dut, fid, dlc, data, True, target)
    assert r["done"]
    assert r["valid"] == 0, "fixed stuff bit polarity is not checked (known gap)"


@cocotb.test(expect_fail=True)
async def test_gap_stuff_count_not_cross_checked(dut):
    """KNOWN GAP: RX never compares the received SC with its own dyn count.

    Here the SC field is rewritten to a wrong value while the CRC is left
    consistent with the ORIGINAL SC, so only a cross-check could catch it.
    Current RX feeds SC into the CRC, so this faults as a CRC error instead of
    a dedicated stuff-count error. Expected to fail until SC is validated.
    """
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await _reset(dut)
    fid, dlc, data = 0x000, 8, [0xFF] * 8
    lay = frame_layout(fid, dlc, data, True)
    assert lay["dyn_count"] > 0
    target = lay["sc_indices"][0]
    r = await _run(dut, fid, dlc, data, True, target)
    assert r["done"]
    assert r["stuff_err"] == 1, \
        "SC mismatch reported as CRC error, not as a stuff-count error (known gap)"
