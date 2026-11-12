import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge

@cocotb.test()
async def test_bit_stuffer_five_ones(dut):
    """Проверяем, что после 5 единиц вставляется 0"""
    clock = Clock(dut.clk, 10, unit="ns")
    cocotb.start_soon(clock.start())
    
    # Сброс
    dut.rst_n.value = 0
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)
    
    # Собираем выходные биты
    output_bits = []
    
    # Подаём 5 единиц и собираем выходы
    for _ in range(5):
        dut.data_in.value = 1
        dut.data_in_valid.value = 1
        await RisingEdge(dut.clk)
        if dut.data_out_valid.value:
            output_bits.append(int(dut.data_out.value))
    
    # Ждём вставку стафф-бита (ещё несколько тактов)
    dut.data_in_valid.value = 0
    for _ in range(5):
        await RisingEdge(dut.clk)
        if dut.data_out_valid.value:
            output_bits.append(int(dut.data_out.value))
    
    # Проверяем, что stuff_count увеличился
    assert dut.stuff_count.value == 1, f"Ожидалось stuff_count=1, получено {dut.stuff_count.value}"
    
    # Проверяем, что выходной поток содержит 6 битов (5 единиц + 1 ноль)
    assert len(output_bits) == 6, f"Ожидалось 6 выходных битов, получено {len(output_bits)}: {output_bits}"
    assert output_bits == [1, 1, 1, 1, 1, 0], f"Ожидалось [1,1,1,1,1,0], получено {output_bits}"

@cocotb.test()
async def test_bit_stuffer_alternating(dut):
    """Проверяем, что чередующиеся биты не вызывают стаффинг"""
    clock = Clock(dut.clk, 10, unit="ns")
    cocotb.start_soon(clock.start())
    
    # Сброс
    dut.rst_n.value = 0
    await RisingEdge(dut.clk)
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)
    
    # Подаём чередующиеся биты
    for i in range(10):
        dut.data_in.value = i % 2
        dut.data_in_valid.value = 1
        await RisingEdge(dut.clk)
    
    # Проверяем, что stuff_count не увеличился
    assert dut.stuff_count.value == 0, f"Ожидалось stuff_count=0, получено {dut.stuff_count.value}"
