"""Unit tests for can_bit_timing.

Periods are measured from simulation timestamps of consecutive pulses.
No edge-skipping heuristics: a single-cycle pulse is observed exactly once
per clock, so delta(t2, t1) / CLK_NS is the true period.
"""
import os
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer
from cocotb.utils import get_sim_time

NBT_PRESCALER = int(os.environ.get("NBT_PRESCALER", "1"))
NBT_TSEG1     = int(os.environ.get("NBT_TSEG1", "12"))
NBT_TSEG2     = int(os.environ.get("NBT_TSEG2", "4"))
DBT_PRESCALER = int(os.environ.get("DBT_PRESCALER", "1"))
DBT_TSEG1     = int(os.environ.get("DBT_TSEG1", "3"))
DBT_TSEG2     = int(os.environ.get("DBT_TSEG2", "1"))
SSP_OFFSET    = int(os.environ.get("SSP_OFFSET", "0"))
CLK_NS = 10

NBT_TICKS = 1 + NBT_TSEG1 + NBT_TSEG2
DBT_TICKS = 1 + DBT_TSEG1 + DBT_TSEG2
NBT_NS    = NBT_PRESCALER * NBT_TICKS * CLK_NS
DBT_NS    = DBT_PRESCALER * DBT_TICKS * CLK_NS


async def reset(dut):
    dut.rst_n.value = 0
    dut.brs_active.value = 0
    dut.sync_edge.value = 0
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)


async def pulse_times(dut, sig_name, count, max_cycles):
    """Collect simulation timestamps of `count` consecutive pulses."""
    sig = getattr(dut, sig_name)
    out = []
    for _ in range(max_cycles):
        await RisingEdge(dut.clk)
        await Timer(1, unit="ns")
        if int(sig.value) == 1:
            out.append(get_sim_time(unit="ns"))
            if len(out) == count:
                return out
    return out


async def measure_periods(dut, sig_name, n_periods, max_cycles):
    ts = await pulse_times(dut, sig_name, n_periods + 1, max_cycles)
    if len(ts) < n_periods + 1:
        return None
    return [(ts[i + 1] - ts[i]) / CLK_NS for i in range(n_periods)]


@cocotb.test()
async def test_dump_timing(dut):
    """Diagnostic: print raw pulse timestamps and deltas for both phases."""
    cocotb.start_soon(Clock(dut.clk, CLK_NS, unit="ns").start())
    await reset(dut)

    for name, brs, ticks, presc in (("NOMINAL", 0, NBT_TICKS, NBT_PRESCALER),
                                    ("DATA",    1, DBT_TICKS, DBT_PRESCALER)):
        dut.brs_active.value = brs
        for _ in range(ticks * presc * 3):
            await RisingEdge(dut.clk)
        for sig in ("sample_en", "bit_boundary"):
            ts = await pulse_times(dut, sig, 5, ticks * presc * 12)
            deltas = [(ts[i + 1] - ts[i]) / CLK_NS for i in range(len(ts) - 1)]
            cocotb.log.info("%s %s: times=%s deltas=%s expected_period=%d",
                            name, sig, ts, deltas, ticks * presc)
        assert len(ts) >= 2, f"{name}: not enough pulses"


@cocotb.test()
async def test_nominal_sample_point(dut):
    cocotb.start_soon(Clock(dut.clk, CLK_NS, unit="ns").start())
    await reset(dut)
    dut.brs_active.value = 0
    for _ in range(NBT_TICKS * NBT_PRESCALER * 2):
        await RisingEdge(dut.clk)

    d = await measure_periods(dut, "sample_en", 3, NBT_TICKS * NBT_PRESCALER * 12)
    assert d is not None, "sample_en did not pulse 4 times"
    exp = NBT_TICKS * NBT_PRESCALER
    assert all(x == exp for x in d), f"nominal sample periods {d}, expected {exp}"


@cocotb.test()
async def test_nominal_bit_boundary(dut):
    cocotb.start_soon(Clock(dut.clk, CLK_NS, unit="ns").start())
    await reset(dut)
    dut.brs_active.value = 0
    for _ in range(NBT_TICKS * NBT_PRESCALER * 2):
        await RisingEdge(dut.clk)

    d = await measure_periods(dut, "bit_boundary", 3, NBT_TICKS * NBT_PRESCALER * 12)
    assert d is not None, "bit_boundary did not pulse 4 times"
    exp = NBT_TICKS * NBT_PRESCALER
    assert all(x == exp for x in d), f"nominal boundary periods {d}, expected {exp}"


@cocotb.test()
async def test_phase_switch_to_data(dut):
    cocotb.start_soon(Clock(dut.clk, CLK_NS, unit="ns").start())
    await reset(dut)

    dut.brs_active.value = 0
    for _ in range(NBT_TICKS * NBT_PRESCALER * 2):
        await RisingEdge(dut.clk)
    assert int(dut.phase.value) == 0

    dut.brs_active.value = 1
    await RisingEdge(dut.clk)
    assert int(dut.phase.value) == 1

    for _ in range(DBT_TICKS * DBT_PRESCALER * 3):
        await RisingEdge(dut.clk)

    d = await measure_periods(dut, "sample_en", 3, DBT_TICKS * DBT_PRESCALER * 12)
    assert d is not None, "sample_en did not pulse 4 times in data phase"
    exp = DBT_TICKS * DBT_PRESCALER
    assert all(x == exp for x in d), f"data sample periods {d}, expected {exp}"


@cocotb.test()
async def test_data_bit_boundary(dut):
    cocotb.start_soon(Clock(dut.clk, CLK_NS, unit="ns").start())
    await reset(dut)
    dut.brs_active.value = 1
    for _ in range(DBT_TICKS * DBT_PRESCALER * 3):
        await RisingEdge(dut.clk)

    d = await measure_periods(dut, "bit_boundary", 3, DBT_TICKS * DBT_PRESCALER * 12)
    assert d is not None, "bit_boundary did not pulse 4 times in data phase"
    exp = DBT_TICKS * DBT_PRESCALER
    assert all(x == exp for x in d), f"data boundary periods {d}, expected {exp}"


@cocotb.test()
async def test_current_bit_time_ns(dut):
    cocotb.start_soon(Clock(dut.clk, CLK_NS, unit="ns").start())
    await reset(dut)

    dut.brs_active.value = 0
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    assert int(dut.current_bit_time_ns.value) == NBT_NS

    dut.brs_active.value = 1
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    assert int(dut.current_bit_time_ns.value) == DBT_NS


@cocotb.test()
async def test_ssp_offset_cycles(dut):
    cocotb.start_soon(Clock(dut.clk, CLK_NS, unit="ns").start())
    await reset(dut)
    assert int(dut.ssp_offset_cycles.value) == (SSP_OFFSET & 0xFF)


@cocotb.test()
async def test_sync_edge_restarts_bit(dut):
    """Resync must restart the bit: boundary comes ~a full bit after sync,
    not the remaining fraction of the interrupted bit."""
    cocotb.start_soon(Clock(dut.clk, CLK_NS, unit="ns").start())
    await reset(dut)
    dut.brs_active.value = 0

    period = NBT_TICKS * NBT_PRESCALER

    # Align to a bit boundary
    ts = await pulse_times(dut, "bit_boundary", 1, period * 6)
    assert ts, "no bit_boundary before sync"

    # Advance into the middle of the next bit
    half = max(1, period // 2)
    for _ in range(half):
        await RisingEdge(dut.clk)

    # Pulse sync for one clock
    dut.sync_edge.value = 1
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")
    t_sync = get_sim_time(unit="ns")
    dut.sync_edge.value = 0

    ts2 = await pulse_times(dut, "bit_boundary", 1, period * 6)
    assert ts2, "no bit_boundary after sync"
    delta = (ts2[0] - t_sync) / CLK_NS

    cocotb.log.info("sync->boundary = %s cycles (period=%d, half=%d)",
                    delta, period, half)
    # Without resync it would be ~period-half. With resync ~period.
    assert delta > period * 0.75, (
        f"sync did not restart bit: {delta} cycles, expected near {period}")
