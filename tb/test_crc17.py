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
async def test_crc17_zeros(dut):
    """CRC для всех нулей должен быть 0."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset_dut(dut)

    for _ in range(8):
        dut.data_in.value = 0
        dut.data_in_valid.value = 1
        await RisingEdge(dut.clk)

    await Timer(1, unit="ns")  # дать NBA примениться
    assert int(dut.crc_out.value) == 0, \
        f"CRC для нулей должен быть 0, получено {int(dut.crc_out.value)}"


@cocotb.test()
async def test_crc17_reference_match(dut):
    """Сравниваем RTL CRC с Python-моделью."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset_dut(dut)

    test_bits = [1, 0, 1, 0, 1, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 0]

    for bit in test_bits:
        dut.data_in.value = bit
        dut.data_in_valid.value = 1
        await RisingEdge(dut.clk)

    # КРИТИЧНО: дождаться применения NBA, иначе читаем значение после (N-1)-го бита
    await Timer(1, unit="ns")

    rtl_crc = int(dut.crc_out.value)

    python_crc_bits = calculate_crc(test_bits, 2)
    python_crc = sum(bit << (16 - i) for i, bit in enumerate(python_crc_bits))

    assert rtl_crc == python_crc, f"RTL CRC ({rtl_crc}) != Python CRC ({python_crc})"


@cocotb.test()
async def test_crc17_incremental(dut):
    """CRC должен меняться на каждом такте с валидным битом."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset_dut(dut)

    test_bits = [1, 1, 1, 1, 1, 0, 0, 0]
    prev_crc = 0

    for i, bit in enumerate(test_bits):
        dut.data_in.value = bit
        dut.data_in_valid.value = 1
        await RisingEdge(dut.clk)
        await Timer(1, unit="ns")
        current_crc = int(dut.crc_out.value)
        if i > 0:
            assert current_crc != prev_crc, f"CRC не изменился на такте {i}"
        prev_crc = current_crc
