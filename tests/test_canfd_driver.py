"""Unit tests for CANFDDriver BRS-aware timing logic."""
import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from canfd_kit.bus.canfd_bus import CANFDDriver
from can_fd_reference import generate_can_fd_frame

class MockSignal:
    def __init__(self):
        self.value = 1
        self.timings = []

    def set(self, val):
        self.value = val

class MockDUT:
    def __init__(self):
        self.rx = MockSignal()
        self.tx = MockSignal()

@pytest.mark.asyncio
async def test_driver_brs_timing_switch():
    """Проверяем, что драйвер переключает скорость при BRS=1, учитывая сдвиг из-за стаффинга."""
    mock_dut = MockDUT()
    driver = CANFDDriver(mock_dut, tx_signal='tx', rx_signal='rx')
    
    arb_time = 2000.0
    data_time = 500.0
    
    # Кадр с BRS=1 (генерирует стафф-бит перед BRS для ID=0x123)
    frame_brs1, brs_idx = generate_can_fd_frame(0x123, 9, [0xAA] * 12, brs=True)
    
    captured_times = []
    async def mock_send_bit(bit: int, bit_time_ns: float):
        captured_times.append(bit_time_ns)
    
    driver.send_bit = mock_send_bit
    await driver.send_frame(frame_brs1, brs_index=brs_idx, brs_enabled=True, 
                            arb_time_ns=arb_time, data_time_ns=data_time)
    
    assert len(captured_times) == len(frame_brs1), "Количество битов не совпадает"
    
    # Биты ДО и ВКЛЮЧАЯ brs_idx идут на арбитражной скорости
    for i in range(brs_idx + 1):
        assert captured_times[i] == arb_time, f"Бит {i} должен быть {arb_time}, получен {captured_times[i]}"
        
    # Биты ПОСЛЕ brs_idx идут на скорости данных
    for i in range(brs_idx + 1, len(frame_brs1)):
        assert captured_times[i] == data_time, f"Бит {i} должен быть {data_time}, получен {captured_times[i]}"

@pytest.mark.asyncio
async def test_driver_no_brs_timing():
    """Проверяем, что при BRS=0 весь кадр идет на арбитражной скорости."""
    mock_dut = MockDUT()
    driver = CANFDDriver(mock_dut, tx_signal='tx', rx_signal='rx')
    
    arb_time = 2000.0
    data_time = 500.0
    
    frame_brs0, brs_idx = generate_can_fd_frame(0x123, 9, [0xAA] * 12, brs=False)
    
    captured_times = []
    async def mock_send_bit(bit: int, bit_time_ns: float):
        captured_times.append(bit_time_ns)
    
    driver.send_bit = mock_send_bit
    await driver.send_frame(frame_brs0, brs_index=brs_idx, brs_enabled=False, 
                            arb_time_ns=arb_time, data_time_ns=data_time)
    
    for i in range(len(frame_brs0)):
        assert captured_times[i] == arb_time, f"Бит {i} должен быть {arb_time}, получен {captured_times[i]}"
