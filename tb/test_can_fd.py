import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge
from can_fd_reference import generate_can_fd_frame

@cocotb.test()
async def test_apb3_read_stub(dut):
    """Проверяем, что APB3 заглушка отвечает на чтение"""
    clock = Clock(dut.clk, 10, unit="ns")
    cocotb.start_soon(clock.start())
    
    # Сброс
    dut.rst_n.value = 0
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)
    
    # APB3 цикл чтения
    dut.psel.value = 1
    dut.penable.value = 0
    dut.pwrite.value = 0
    dut.paddr.value = 32'h00000000
    await RisingEdge(dut.clk)
    
    dut.penable.value = 1
    await RisingEdge(dut.clk)
    
    # Проверяем, что заглушка вернула наш тестовый паттерн
    assert dut.pready.value == 1, "PREADY не установлен"
    assert dut.prdata.value == 0xDEADBEEF, f"Ожидалось 0xDEADBEEF, получено {hex(dut.prdata.value)}"
    
    dut.psel.value = 0
    dut.penable.value = 0

@cocotb.test()
async def test_reference_model_integration(dut):
    """Проверяем, что Python-модель генерирует кадр корректно"""
    frame = generate_can_fd_frame(id=0x123, dlc=9, data=[0xAA]*12, brs=True)
    
    # Просто проверяем длину и первые биты (SOF=0, ID=0x123)
    assert len(frame) == 145, f"Ожидалось 145 бит, получено {len(frame)}"
    assert frame[0] == 0, "SOF должен быть 0 (dominant)"
    assert frame[1:12] == [0,0,1,0,0,1,0,0,0,1,1], "ID 0x123 не совпадает"
