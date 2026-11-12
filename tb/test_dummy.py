import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge

@cocotb.test()
async def test_dummy_increment(dut):
    # Запускаем тактовый генератор (исправлен warning: units -> unit)
    clock = Clock(dut.clk, 10, unit="ns")
    cocotb.start_soon(clock.start())
    
    # Сброс
    dut.rst.value = 1
    dut.data_in.value = 0
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut.rst.value = 0
    
    # Даём схеме пару тактов после сброса
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    
    # Тест: подаём значения и проверяем результат
    for i in range(5):
        dut.data_in.value = i
        await RisingEdge(dut.clk)
        await RisingEdge(dut.clk)  # <--- ДОБАВЛЕН ВТОРОЙ ТАКТ
        assert dut.data_out.value == (i + 1) % 256, f"Ошибка: ожидалось {(i+1)%256}, получено {dut.data_out.value}"
