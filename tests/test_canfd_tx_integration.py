"""Integration: CANFDMonitor captures the DUT bit stream and compares it
against the ISO reference model, bit for bit.
"""
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer

from canfd_kit.bus.canfd_bus import CANFDMonitor
from can_fd_reference import generate_can_fd_frame, dlc_len


async def _reset(dut):
    dut.rst_n.value = 0
    dut.tx_start.value = 0
    dut.tx_data.value = 0  # <-- Сбрасываем как целое число
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)


async def _run_case(dut, fid, dlc, data, brs):
    monitor = CANFDMonitor(dut, "tx_bit", "tx_bit_valid")
    task = cocotb.start_soon(monitor.capture_frame())

    n = dlc_len(dlc)
    dut.tx_id.value = fid
    dut.tx_dlc.value = dlc
    dut.tx_brs.value = 1 if brs else 0
    
    if n:
        # Присваиваем плоскому 512-битному вектору как целому числу (MSB first)
        payload = int.from_bytes(bytes(data[:n]), "big")
        dut.tx_data.value = payload << (512 - 8 * n)
    else:
        dut.tx_data.value = 0

    dut.tx_start.value = 1
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")
    dut.tx_start.value = 0

    captured = await task
    ref = generate_can_fd_frame(fid, dlc, list(data[:n]), bool(brs))

    assert len(captured) == len(ref), \
        f"length mismatch: captured {len(captured)}, reference {len(ref)}"
    if captured != ref:
        idx = next(i for i, (a, b) in enumerate(zip(captured, ref)) if a != b)
        raise AssertionError(f"first bit mismatch at index {idx}")
    cocotb.log.info(f"verified frame: {len(captured)} bits, dlc={dlc}, brs={brs}")


@cocotb.test()
async def test_monitor_aa12(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await _reset(dut)
    await _run_case(dut, 0x123, 9, [0xAA] * 12, True)


@cocotb.test()
async def test_monitor_zero12(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await _reset(dut)
    await _run_case(dut, 0x123, 9, [0x00] * 12, True)


@cocotb.test()
async def test_monitor_ff64(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await _reset(dut)
    await _run_case(dut, 0x7FF, 15, [0xFF] * 64, True)
