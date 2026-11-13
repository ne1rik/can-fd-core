"""Comprehensive loopback tests: all DLC, various IDs, data patterns, BRS settings."""
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
    assert int(dut.rx_done.value) == 1, f"RX не завершил приём (DLC={dlc}, ID=0x{fid:03X})"
    assert int(dut.rx_valid.value) == 1, (
        f"RX error (DLC={dlc}, ID=0x{fid:03X}): crc_err={int(dut.rx_crc_err.value)} "
        f"stuff_err={int(dut.rx_stuff_err.value)}"
    )
    assert int(dut.rx_id.value) == fid, f"ID mismatch: {int(dut.rx_id.value)} != {fid}"
    assert int(dut.rx_dlc.value) == dlc, f"DLC mismatch: {int(dut.rx_dlc.value)} != {dlc}"
    
    # Проверяем данные
    rx_data_int = int(dut.rx_data.value)
    for i in range(n):
        rx_byte = (rx_data_int >> (512 - 8*(i+1))) & 0xFF
        assert rx_byte == data[i], f"Data mismatch at byte {i}: {rx_byte} != {data[i]}"


# DLC 0–8: классический CAN
@cocotb.test()
async def test_dlc_0_id_000(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await _run_loopback(dut, 0x000, 0, [], brs=True)

@cocotb.test()
async def test_dlc_1_id_123(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await _run_loopback(dut, 0x123, 1, [0x55], brs=True)

@cocotb.test()
async def test_dlc_2_id_5AA(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await _run_loopback(dut, 0x5AA, 2, [0xAA, 0x55], brs=True)

@cocotb.test()
async def test_dlc_3_id_7FF(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await _run_loopback(dut, 0x7FF, 3, [0xFF, 0x00, 0xAA], brs=True)

@cocotb.test()
async def test_dlc_4_id_100(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await _run_loopback(dut, 0x100, 4, [0x12, 0x34, 0x56, 0x78], brs=True)

@cocotb.test()
async def test_dlc_5_id_200(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await _run_loopback(dut, 0x200, 5, [0xDE, 0xAD, 0xBE, 0xEF, 0xCA], brs=True)

@cocotb.test()
async def test_dlc_6_id_300(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await _run_loopback(dut, 0x300, 6, [0x01, 0x23, 0x45, 0x67, 0x89, 0xAB], brs=True)

@cocotb.test()
async def test_dlc_7_id_400(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await _run_loopback(dut, 0x400, 7, [0xFE, 0xDC, 0xBA, 0x98, 0x76, 0x54, 0x32], brs=True)

@cocotb.test()
async def test_dlc_8_id_500(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await _run_loopback(dut, 0x500, 8, [0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88], brs=True)

# DLC 9–15: CAN FD
@cocotb.test()
async def test_dlc_9_id_123_brs1(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await _run_loopback(dut, 0x123, 9, [0xAA] * 12, brs=True)

@cocotb.test()
async def test_dlc_10_id_234_brs0(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await _run_loopback(dut, 0x234, 10, [0x55] * 16, brs=False)

@cocotb.test()
async def test_dlc_11_id_345_crc21_boundary(dut):
    """DLC=11 (20 bytes) — граница CRC-17/21."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await _run_loopback(dut, 0x345, 11, [0xFF] * 20, brs=True)

@cocotb.test()
async def test_dlc_12_id_456_crc21(dut):
    """DLC=12 (24 bytes) — CRC-21."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await _run_loopback(dut, 0x456, 12, [0x00] * 24, brs=True)

@cocotb.test()
async def test_dlc_13_id_567_crc21(dut):
    """DLC=13 (32 bytes) — CRC-21."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await _run_loopback(dut, 0x567, 13, [0xAA, 0x55] * 16, brs=True)

@cocotb.test()
async def test_dlc_14_id_678_crc21(dut):
    """DLC=14 (48 bytes) — CRC-21."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await _run_loopback(dut, 0x678, 14, [0xFF, 0x00, 0xAA, 0x55] * 12, brs=True)

@cocotb.test()
async def test_dlc_15_id_7FF_crc21(dut):
    """DLC=15 (64 bytes) — CRC-21, максимальная длина."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await _run_loopback(dut, 0x7FF, 15, [i & 0xFF for i in range(64)], brs=True)

# Edge cases: паттерны, гарантированно создающие стафф-биты
@cocotb.test()
async def test_dlc_8_all_zeros(dut):
    """8 байт 0x00 — много нулей, много стафф-битов."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await _run_loopback(dut, 0x000, 8, [0x00] * 8, brs=True)

@cocotb.test()
async def test_dlc_8_all_ones(dut):
    """8 байт 0xFF — много единиц, много стафф-битов."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await _run_loopback(dut, 0x7FF, 8, [0xFF] * 8, brs=True)

@cocotb.test()
async def test_dlc_12_alternating(dut):
    """24 байта чередующихся 0xAA/0x55."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await _run_loopback(dut, 0x555, 12, [0xAA if i % 2 == 0 else 0x55 for i in range(24)], brs=True)

@cocotb.test()
async def test_dlc_15_mixed_patterns(dut):
    """64 байта смешанных паттернов."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    data = [0xFF] * 16 + [0x00] * 16 + [0xAA] * 16 + [0x55] * 16
    await _run_loopback(dut, 0x333, 15, data, brs=True)
