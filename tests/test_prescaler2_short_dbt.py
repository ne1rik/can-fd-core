"""D5 regression test: sync_edge must survive blind prescaler clocks.

Configuration under test (set via Makefile.bittiming parameters):
    NBT_PRESCALER=2, NBT_TSEG1=12, NBT_TSEG2=4
    DBT_PRESCALER=2, DBT_TSEG1=1,  DBT_TSEG2=1   (DBT = 3 ticks = 6 clocks)

Pre-fix defect: `sync_edge` is sampled only inside the `tick_en` branch of
`can_bit_timing`. With prescaler 2 a tick happens every second clock, so a
one-clock sync pulse landing on a "blind" clock (clk_cnt != prescaler-1) is
dropped. The receiver then misses hard synchronisation on short data phases
and long frames desynchronise (timing-matrix timeouts).

The fix restarts the bit sequencer on the sync clock itself (tseg_cnt only,
prescaler phase preserved) and masks stale pre-sync sample strobes. This
test pins the corrected behaviour:
  - a mid-bit sync pulse on a blind clock restarts the bit (tseg_cnt -> 0);
  - the next bit_boundary arrives exactly one restarted bit after the sync,
    not at the stale position of the interrupted bit.
"""
import os
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer
from cocotb.utils import get_sim_time

NBT_PRESCALER = int(os.environ.get("NBT_PRESCALER", "2"))
NBT_TSEG1     = int(os.environ.get("NBT_TSEG1", "12"))
NBT_TSEG2     = int(os.environ.get("NBT_TSEG2", "4"))
DBT_PRESCALER = int(os.environ.get("DBT_PRESCALER", "2"))
DBT_TSEG1     = int(os.environ.get("DBT_TSEG1", "1"))
DBT_TSEG2     = int(os.environ.get("DBT_TSEG2", "1"))
CLK_NS = 10

NBT_TICKS = 1 + NBT_TSEG1 + NBT_TSEG2
DBT_TICKS = 1 + DBT_TSEG1 + DBT_TSEG2
NBT_PERIOD = NBT_TICKS * NBT_PRESCALER   # clocks per nominal bit
DBT_PERIOD = DBT_TICKS * DBT_PRESCALER   # clocks per data bit


async def reset(dut):
    dut.rst_n.value = 0
    dut.brs_active.value = 0
    dut.sync_edge.value = 0
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)


async def pulse_time(dut, sig_name, max_cycles):
    """Timestamp (ns) of the next pulse of sig_name, or None."""
    sig = getattr(dut, sig_name)
    for _ in range(max_cycles):
        await RisingEdge(dut.clk)
        await Timer(1, unit="ns")
        if int(sig.value) == 1:
            return get_sim_time(unit="ns")
    return None


async def sync_mid_bit_blind(dut, prescaler):
    """Wait one bit_boundary for alignment, then pulse sync_edge for exactly
    one clock in the middle of the next bit, on a BLIND clock (clk_cnt !=
    prescaler-1, tseg_cnt == 1). Returns (t_sync, blind clk_cnt, pre-sync
    tseg_cnt)."""
    period = DBT_PERIOD if int(dut.brs_active.value) else NBT_PERIOD
    t_b = await pulse_time(dut, "bit_boundary", period * 6)
    assert t_b is not None, "no bit_boundary for alignment"

    # The boundary tick reset clk_cnt to 0, so advancing exactly `prescaler`
    # clocks lands on a blind clock (clk_cnt == 0) with tseg_cnt == 1: the
    # first tick of the bit already ran, i.e. truly mid-bit.
    for _ in range(prescaler):
        await RisingEdge(dut.clk)
    await Timer(1, unit="ns")
    clk_v = int(dut.clk_cnt.value)
    tseg_v = int(dut.tseg_cnt.value)
    assert clk_v != prescaler - 1, (
        f"sync probe landed on tick clock (clk_cnt={clk_v}) - blind clock required")
    assert tseg_v >= 1, f"probe not mid-bit (tseg_cnt={tseg_v})"

    dut.sync_edge.value = 1
    t_sync = get_sim_time(unit="ns")
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")
    dut.sync_edge.value = 0
    return t_sync, clk_v, tseg_v


def expected_restart_delta(tseg_v, clk_v, prescaler, ticks):
    """Clocks from the sync pulse to the next visible bit_boundary when the
    bit is restarted on the sync clock itself: the prescaler keeps its
    phase, so the first tick of the restarted bit lands
    (prescaler - 1 - clk_v) clocks after the restart edge, and the fresh
    bit then runs `ticks` ticks before its boundary pulse becomes visible."""
    first_tick = prescaler - 1 - clk_v   # clocks from restart edge to 1st tick
    return (1 + first_tick + (ticks - 1) * prescaler) * CLK_NS


async def run_sync_case(dut, brs, ticks, period, prescaler):
    dut.brs_active.value = int(brs)
    # A few free-running bits first: the config must be healthy on its own.
    t1 = await pulse_time(dut, "bit_boundary", period * 4)
    t2 = await pulse_time(dut, "bit_boundary", period * 4)
    assert t1 is not None and t2 is not None, "free-running boundary missing"
    d = (t2 - t1) / CLK_NS
    assert d == period, f"free-running boundary period {d}, expected {period}"

    t_sync, clk_v, tseg_v = await sync_mid_bit_blind(dut, prescaler)

    # The restart takes effect on the edge ending the sync clock: tseg_cnt
    # is 0 for exactly the one clock that follows the pulse. We are now one
    # clock past that edge (the awaited edge inside sync_mid_bit_blind).
    await Timer(1, unit="ns")
    tseg_after = int(dut.tseg_cnt.value)
    assert tseg_after == 0, (
        f"sync lost: tseg_cnt={tseg_after} after mid-bit sync "
        f"(clk_cnt={clk_v}, pre-sync tseg_cnt={tseg_v})")

    t_next = await pulse_time(dut, "bit_boundary", period * 4)
    assert t_next is not None, "no bit_boundary after sync"
    delta = t_next - t_sync
    exp = expected_restart_delta(tseg_v, clk_v, prescaler, ticks)
    cocotb.log.info("brs=%d sync@tseg=%d clk=%d -> boundary delta=%d ns, expected %d ns",
                    int(brs), tseg_v, clk_v, delta, exp)
    assert delta == exp, (
        f"bit not restarted: sync->boundary {delta} ns, expected {exp} ns "
        f"(stale-bit continuation would be shorter)")


@cocotb.test()
async def test_free_running_prescaler2(dut):
    """Sanity: with prescaler=2 both phases pulse at the configured periods."""
    cocotb.start_soon(Clock(dut.clk, CLK_NS, unit="ns").start())
    await reset(dut)

    dut.brs_active.value = 0
    for sig in ("sample_en", "bit_boundary"):
        ts = []
        for _ in range(3):
            t = await pulse_time(dut, sig, NBT_PERIOD * 6)
            assert t is not None, f"nominal {sig} missing"
            ts.append(t)
        per = [(ts[i + 1] - ts[i]) / CLK_NS for i in range(2)]
        assert all(x == NBT_PERIOD for x in per), f"nominal {sig} periods {per}"

    dut.brs_active.value = 1
    for sig in ("sample_en", "bit_boundary"):
        ts = []
        for _ in range(3):
            t = await pulse_time(dut, sig, DBT_PERIOD * 6)
            assert t is not None, f"data {sig} missing"
            ts.append(t)
        per = [(ts[i + 1] - ts[i]) / CLK_NS for i in range(2)]
        assert all(x == DBT_PERIOD for x in per), f"data {sig} periods {per}"


@cocotb.test()
async def test_sync_blind_tick_restarts_data_bit(dut):
    """DATA phase, prescaler=2, DBT=3 ticks: sync on a blind clock must
    reset tseg_cnt and delay bit_boundary by a full restarted bit."""
    cocotb.start_soon(Clock(dut.clk, CLK_NS, unit="ns").start())
    await reset(dut)
    await run_sync_case(dut, brs=True, ticks=DBT_TICKS,
                        period=DBT_PERIOD, prescaler=DBT_PRESCALER)


@cocotb.test()
async def test_sync_blind_tick_restarts_nominal_bit(dut):
    """NOMINAL phase, prescaler=2: same blind-clock scenario on the long bit."""
    cocotb.start_soon(Clock(dut.clk, CLK_NS, unit="ns").start())
    await reset(dut)
    await run_sync_case(dut, brs=False, ticks=NBT_TICKS,
                        period=NBT_PERIOD, prescaler=NBT_PRESCALER)


@cocotb.test()
async def test_sync_on_tick_clock_still_works(dut):
    """Compatibility guard: a sync pulse that coincides with a tick clock is
    the pre-existing supported path and must keep working after the fix."""
    cocotb.start_soon(Clock(dut.clk, CLK_NS, unit="ns").start())
    await reset(dut)
    dut.brs_active.value = 1

    t_b = await pulse_time(dut, "bit_boundary", DBT_PERIOD * 6)
    assert t_b is not None, "no bit_boundary for alignment"
    # Offset 2*prescaler-1 from the boundary pulse is a tick clock
    # (clk_cnt == prescaler-1) and mid-bit (tseg_cnt == 1 was set by the
    # first tick of the bit).
    for _ in range(2 * DBT_PRESCALER - 1):
        await RisingEdge(dut.clk)
    await Timer(1, unit="ns")
    assert int(dut.clk_cnt.value) == DBT_PRESCALER - 1, "probe not on tick clock"
    assert int(dut.tseg_cnt.value) >= 1, "probe not mid-bit"

    dut.sync_edge.value = 1
    t_sync = get_sim_time(unit="ns")
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")
    dut.sync_edge.value = 0

    t_next = await pulse_time(dut, "bit_boundary", DBT_PERIOD * 6)
    assert t_next is not None, "no bit_boundary after sync"
    exp = (1 + DBT_TICKS * DBT_PRESCALER) * CLK_NS  # consumed on the sync clock itself: prescaler - clk_v == 1
    delta = t_next - t_sync
    cocotb.log.info("on-tick sync -> delta=%d ns, expected %d ns", delta, exp)
    assert delta == exp, f"on-tick sync broken: {delta} ns, expected {exp} ns"
