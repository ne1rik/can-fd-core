"""Verify that sync_edge resets tseg_cnt mid-bit without breaking the boundary."""
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer

@cocotb.test()
async def test_sjw_resync_midbit(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    dut.rst_n.value = 0
    dut.brs_active.value = 0
    dut.sync_edge.value = 0
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut.rst_n.value = 1
    
    # Ждем первого bit_boundary
    for _ in range(50):
        await RisingEdge(dut.clk)
        if int(dut.bit_boundary.value) == 1:
            break
            
    # Продвигаемся на 5 тактов внутрь бита
    for _ in range(5):
        await RisingEdge(dut.clk)
        await Timer(1, 'ns')  # Даем время на NBA
        
    tseg_before = int(dut.tseg_cnt.value)
    cocotb.log.info(f"tseg_cnt before sync: {tseg_before}")
    
    # Правильная синхронизация: устанавливаем sync_edge ДО rising edge
    dut.sync_edge.value = 1
    await RisingEdge(dut.clk)  # В этом такте sync_edge=1 на момент posedge
    await Timer(2, 'ns')  # Даем время на NBA обновление регистров
    tseg_after = int(dut.tseg_cnt.value)
    dut.sync_edge.value = 0
    
    cocotb.log.info(f"tseg_cnt after sync: {tseg_after}")
    
    # При prescaler=1 tick_en истинен каждый такт, поэтому sync_edge проверяется каждый такт
    assert tseg_after == 0, f"Expected tseg_cnt reset to 0, got {tseg_after}"
    
    # Проверяем, что bit_boundary всё равно наступит позже
    boundary_hit = False
    for _ in range(30):
        await RisingEdge(dut.clk)
        if int(dut.bit_boundary.value) == 1:
            boundary_hit = True
            break
            
    assert boundary_hit, "bit_boundary never arrived after resync"
    cocotb.log.info("SJW resync successfully reset counter and boundary arrived")
