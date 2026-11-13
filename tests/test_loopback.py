"""Loopback test: TX -> Wire -> RX via wrapper."""
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from can_fd_reference import generate_can_fd_frame, dlc_len


@cocotb.test()
async def test_loopback_basic(dut):
    """
    Loopback-тест через wrapper: TX отправляет кадр, RX его принимает.
    Проверяем, что ID, DLC и данные совпадают.
    """
    # Запуск тактовой частоты
    clock = Clock(dut.clk, 10, unit="ns")
    cocotb.start_soon(clock.start())
    
    # Сброс
    dut.rst_n.value = 0
    dut.tx_start.value = 0
    dut.tx_data.value = 0
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)
    
    # Генерируем кадр
    fid = 0x123
    dlc = 9
    data = [0xAA] * 12
    frame = generate_can_fd_frame(fid, dlc, data, brs=True)
    
    # Запускаем передачу
    dut.tx_id.value = fid
    dut.tx_dlc.value = dlc
    dut.tx_brs.value = 1
    
    payload = int.from_bytes(bytes(data), "big")
    dut.tx_data.value = payload << (512 - 8 * dlc_len(dlc))
    
    dut.tx_start.value = 1
    await RisingEdge(dut.clk)
    dut.tx_start.value = 0
    
    # Ждём завершения приёма (RX сам читает с bus_wire)
    for _ in range(2000):
        await RisingEdge(dut.clk)
        if int(dut.rx_done.value) == 1:
            break
    
    # Проверяем результаты
    assert int(dut.rx_done.value) == 1, "RX не завершил приём"
    assert int(dut.rx_valid.value) == 1, f"RX сообщает об ошибке: crc_err={int(dut.rx_crc_err.value)}, stuff_err={int(dut.rx_stuff_err.value)}"
    assert int(dut.rx_id.value) == fid, f"ID mismatch: {int(dut.rx_id.value)} != {fid}"
    assert int(dut.rx_dlc.value) == dlc, f"DLC mismatch: {int(dut.rx_dlc.value)} != {dlc}"
    
    # Проверяем данные (первые N байт)
    rx_data_int = int(dut.rx_data.value)
    for i in range(dlc_len(dlc)):
        rx_byte = (rx_data_int >> (512 - 8*(i+1))) & 0xFF
        assert rx_byte == data[i], f"Data mismatch at byte {i}: {rx_byte} != {data[i]}"
    
    cocotb.log.info(f"Loopback OK: ID=0x{fid:03X}, DLC={dlc}, {dlc_len(dlc)} bytes")
