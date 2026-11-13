"""Extended loopback tests: various DLC, data patterns, BRS settings."""
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from can_fd_reference import generate_can_fd_frame, dlc_len


async def _run_loopback(dut, fid, dlc, data, brs):
    """Helper: run a single loopback case and verify."""
    # Сброс
    dut.rst_n.value = 0
    dut.tx_start.value = 0
    dut.tx_data.value = 0
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)
    
    # Запускаем передачу
    dut.tx_id.value = fid
    dut.tx_dlc.value = dlc
    dut.tx_brs.value = 1 if brs else 0
    
    n = dlc_len(dlc)
    if n:
        payload = int.from_bytes(bytes(data[:n]), "big")
        dut.tx_data.value = payload << (512 - 8 * n)
    
    dut.tx_start.value = 1
    await RisingEdge(dut.clk)
    dut.tx_start.value = 0
    
    # Ждём завершения приёма
    for _ in range(3000):
        await RisingEdge(dut.clk)
        if int(dut.rx_done.value) == 1:
            break
    
    # Проверяем результаты
    assert int(dut.rx_done.value) == 1, f"RX не завершил приём (DLC={dlc})"
    assert int(dut.rx_valid.value) == 1, (
        f"RX error (DLC={dlc}): crc_err={int(dut.rx_crc_err.value)} "
        f"stuff_err={int(dut.rx_stuff_err.value)}"
    )
    assert int(dut.rx_id.value) == fid, f"ID mismatch: {int(dut.rx_id.value)} != {fid}"
    assert int(dut.rx_dlc.value) == dlc, f"DLC mismatch: {int(dut.rx_dlc.value)} != {dlc}"
    
    # Проверяем данные
    rx_data_int = int(dut.rx_data.value)
    for i in range(n):
        rx_byte = (rx_data_int >> (512 - 8*(i+1))) & 0xFF
        assert rx_byte == data[i], f"Data mismatch at byte {i}: {rx_byte} != {data[i]}"


@cocotb.test()
async def test_loopback_dlc_0(dut):
    """DLC=0 (no data)."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await _run_loopback(dut, 0x100, 0, [], brs=True)


@cocotb.test()
async def test_loopback_dlc_8(dut):
    """DLC=8 (classic CAN length)."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await _run_loopback(dut, 0x200, 8, [0x55] * 8, brs=True)


@cocotb.test()
async def test_loopback_dlc_15_brs0(dut):
    """DLC=15 (64 bytes), BRS=0 (no bit rate switch)."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await _run_loopback(dut, 0x7FF, 15, [0xFF] * 64, brs=False)


@cocotb.test()
async def test_loopback_dlc_12_mixed(dut):
    """DLC=12 (24 bytes), mixed data pattern."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    data = [i & 0xFF for i in range(24)]
    await _run_loopback(dut, 0x555, 12, data, brs=True)
