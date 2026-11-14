"""Test that can_bit_timing works in backward compatibility mode (TSEG=0)."""
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge

@cocotb.test()
async def test_backward_compat(dut):
    """At TSEG=0, bit_boundary and sample_en should pulse every clock."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    
    dut.rst_n.value = 0
    dut.brs_active.value = 0
    dut.sync_edge.value = 0
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)
    
    # Count pulses in 20 clocks
    boundary_count = 0
    sample_count = 0
    for _ in range(20):
        await RisingEdge(dut.clk)
        if int(dut.bit_boundary.value) == 1:
            boundary_count += 1
        if int(dut.sample_en.value) == 1:
            sample_count += 1
    
    cocotb.log.info(f"bit_boundary pulses: {boundary_count}/20")
    cocotb.log.info(f"sample_en pulses: {sample_count}/20")
    
    # At TSEG=0, should pulse every clock
    assert boundary_count >= 18, f"Expected ~20 boundary pulses, got {boundary_count}"
    assert sample_count >= 18, f"Expected ~20 sample pulses, got {sample_count}"
