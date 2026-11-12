import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer
from can_fd_reference import calculate_crc


async def reset_dut(dut):
    dut.rst_n.value = 0
    dut.crc_reset.value = 1
    await RisingEdge(dut.clk)
    dut.rst_n.value = 1
    dut.crc_reset.value = 0
    await RisingEdge(dut.clk)


@cocotb.test()
async def test_crc21_reference_match(dut):
    """Сравниваем RTL CRC-21 с Python-моделью для payload >= 20 байт."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset_dut(dut)
    
    # 24 бита для теста (имитация части кадра с payload >= 20 байт)
    test_bits = [1, 0, 1, 0, 1, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 0, 1, 1, 0, 0, 1, 0, 1, 1]
    
    for bit in test_bits:
        dut.data_in.value = bit
        dut.data_in_valid.value = 1
        await RisingEdge(dut.clk)
    
    await Timer(1, unit="ns")
    
    rtl_crc = int(dut.crc_out.value)
    
    # Python-модель: 20 байт = CRC-21
    python_crc_bits = calculate_crc(test_bits, 20)
    python_crc = sum(bit << (20 - i) for i, bit in enumerate(python_crc_bits))
    
    assert rtl_crc == python_crc, f"RTL CRC-21 ({rtl_crc}) != Python CRC-21 ({python_crc})"
