"""Prove whether can_bit_timing survives a phase switch mid-bit.

NBT = 1+12+4 = 17 ticks, DBT = 1+3+1 = 5 ticks.
Switch brs_active when tseg_cnt is already past the new DBT total.
A correct controller must produce the next bit_boundary within ~one DBT bit.
"""
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge
from cocotb.utils import get_sim_time


async def wait_pulse(dut, sig, limit):
    for _ in range(limit):
        await RisingEdge(dut.clk)
        if int(sig.value) == 1:
            return get_sim_time(unit="ns")
    return None


@cocotb.test()
async def test_phase_switch_midbit(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    dut.rst_n.value = 0
    dut.brs_active.value = 0
    dut.sync_edge.value = 0
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut.rst_n.value = 1

    t_b = await wait_pulse(dut, dut.bit_boundary, 200)
    assert t_b is not None, "no nominal boundary at all"
    cocotb.log.info("nominal boundary @%s ns", t_b)

    # Advance deep into the nominal bit: past DBT sample_tick(4) and total-1(4)
    for _ in range(14):
        await RisingEdge(dut.clk)
    cnt_before = int(dut.tseg_cnt.value)
    t0 = get_sim_time(unit="ns")
    dut.brs_active.value = 1
    cocotb.log.info("switch phase: tseg_cnt=%d @%s ns (DBT total=5)", cnt_before, t0)

    t_next = await wait_pulse(dut, dut.bit_boundary, 600)
    if t_next is None:
        cocotb.log.error("NO boundary within 600 clocks after phase switch")
        raise AssertionError("phase switch killed the bit counter")
    dt = t_next - t0
    cocotb.log.info("next boundary after switch: dt=%.1f ns (%.1f clocks)", dt, dt / 10)

    # Collect following sample periods
    times = []
    for _ in range(6):
        t = await wait_pulse(dut, dut.sample_en, 600)
        if t is None:
            break
        times.append(t)
    deltas = [times[i + 1] - times[i] for i in range(len(times) - 1)]
    cocotb.log.info("data-phase sample deltas=%s (expect 50 ns)", deltas)

    assert dt <= 70.0, f"boundary took {dt} ns, expected <= ~50-60 ns (one DBT bit)"
    assert deltas and all(abs(d - 50.0) < 1e-6 for d in deltas), \
        f"data-phase sample period wrong: {deltas}"
