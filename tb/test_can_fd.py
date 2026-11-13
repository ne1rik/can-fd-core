"""Auxiliary regression: APB3 stub + ISO reference-model anchors + CTRL polarity lock.

Run with:  make -f Makefile.aux

Frame-length anchors are wire-bit counts for ISO 11898-1:2015 framing
(dynamic stuffing + stuff count + fixed stuff bits + 10-bit tail).
Status of anchor V-001 (CRC-17 = 0x006BD): third-party-reported, source
StackOverflow q/76852533; pending CTU cross-check before promotion to
primary-confirmed. See docs/vectors_provenance.md.
"""

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer

from can_fd_reference import generate_can_fd_frame, dlc_len

ANCHOR_5AA_8xFF_LEN = 135
FRAME_123_DLC9_AA_LEN = 155


@cocotb.test()
async def test_apb3_read_stub(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    dut.rst_n.value = 0
    dut.psel.value = 0
    dut.penable.value = 0
    dut.pwrite.value = 0
    dut.paddr.value = 0
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)

    dut.psel.value = 1
    dut.penable.value = 0
    await RisingEdge(dut.clk)
    dut.penable.value = 1
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")

    assert int(dut.pready.value) == 1, "PREADY not asserted"
    got = int(dut.prdata.value)
    assert got == 0xDEADBEEF, f"expected 0xDEADBEEF, got {hex(got)}"

    dut.psel.value = 0
    dut.penable.value = 0


@cocotb.test()
async def test_reference_model_anchors(dut):
    anchor = generate_can_fd_frame(0x5AA, 8, [0xFF] * 8, True)
    assert len(anchor) == ANCHOR_5AA_8xFF_LEN, f"anchor len {len(anchor)}"

    frame = generate_can_fd_frame(0x123, 9, [0xAA] * 12, True)
    assert len(frame) == FRAME_123_DLC9_AA_LEN, f"frame len {len(frame)}"
    assert frame[0] == 0, "SOF must be dominant"
    assert frame[1:12] == [(0x123 >> i) & 1 for i in range(10, -1, -1)], "ID mismatch"

    assert dlc_len(9) == 12
    assert dlc_len(12) == 24
    assert dlc_len(15) == 64


@cocotb.test()
async def test_control_field_polarity(dut):
    """Lock ISO FBFF control-field polarities.

    Layout: SOF(1) | ID(11) | RRS IDE FDF res BRS ESI (6) | DLC(4) | DATA.
    For 0xAA pattern no dynamic stuff bit is inserted in the header
    (dyn_stuff=0, raw=118), so frame indices equal raw indices.
    BRS must be RECESSIVE (1) when the second bit rate is used (CiA/ISO).
    """
    switching = generate_can_fd_frame(0x123, 9, [0xAA] * 12, True)
    nominal = generate_can_fd_frame(0x123, 9, [0xAA] * 12, False)

    assert switching[12:18] == [0, 0, 1, 0, 1, 0], f"CTRL={switching[12:18]}"
    assert nominal[12:18] == [0, 0, 1, 0, 0, 0], f"CTRL={nominal[12:18]}"
    assert switching[16] == 1, "BRS must be recessive when switching bit rate"
