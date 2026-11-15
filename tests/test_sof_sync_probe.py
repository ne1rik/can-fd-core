"""Does the SOF hard-sync pulse reach the bit counter and reset it?"""
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer
from cocotb.utils import get_sim_time
from can_fd_reference import generate_can_fd_frame, dlc_len


def h(dut, path, required=True):
    cur = dut
    for part in path.split("."):
        if not hasattr(cur, part):
            if required:
                raise AssertionError(f"MISSING HANDLE: {path}")
            cocotb.log.warning("MISSING HANDLE: %s", path)
            return None
        cur = getattr(cur, part)
    cocotb.log.info("handle ok: %s", path)
    return cur


@cocotb.test()
async def test_sof_sync_probe(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    dut.rst_n.value = 0
    dut.tx_start.value = 0
    dut.tx_data.value = 0
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)

    sof     = h(dut, "u_rx.sof_sync")
    syn_in  = h(dut, "u_rx.u_timing.sync_edge")
    cnt     = h(dut, "u_rx.u_timing.tseg_cnt")
    rxd     = h(dut, "u_rx.rx_bit_d")
    rstate  = h(dut, "u_rx.state")
    strb    = h(dut, "u_rx.rx_sample_strobe")

    fid, dlc = 0x16b, 8
    data = [0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88]
    n = dlc_len(dlc, classic=False)
    ref = generate_can_fd_frame(fid, dlc, data, True, extended=False, classic=False)

    events = []
    sof_t, syn_t, strb_t = [], [], []

    async def mon():
        prev_bus = 1
        while True:
            await RisingEdge(dut.clk)
            await Timer(1, unit="ns")
            t = get_sim_time(unit="ns")
            bus = int(dut.tx_bit.value)
            if prev_bus == 1 and bus == 0 and len(events) < 40:
                events.append(("BUS_FALL", t, int(cnt.value), int(rstate.value), int(rxd.value)))
            prev_bus = bus
            if int(sof.value) == 1:
                sof_t.append(t)
                events.append(("SOF_SYNC", t, int(cnt.value), int(rstate.value), int(rxd.value)))
            if int(syn_in.value) == 1:
                syn_t.append(t)
                events.append(("SYNC_IN", t, int(cnt.value), int(rstate.value), int(rxd.value)))
            if int(strb.value) == 1 and len(strb_t) < 6:
                strb_t.append(t)
                events.append(("STROBE", t, int(cnt.value), int(rstate.value), int(rxd.value)))

    m = cocotb.start_soon(mon())
    dut.tx_id.value = fid
    dut.tx_dlc.value = dlc
    dut.tx_brs.value = 1
    dut.tx_data.value = int.from_bytes(bytes(data), "big") << (512 - 8 * n)
    dut.tx_start.value = 1
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")
    dut.tx_start.value = 0

    # Run well past SOF: do NOT stop on free-running pre-frame strobes.
    for _ in range(4000):
        await RisingEdge(dut.clk)
        await Timer(1, unit="ns")
    m.cancel()

    cocotb.log.info("sof_sync pulses: %s", sof_t[:8])
    cocotb.log.info("timing.sync_edge pulses: %s", syn_t[:8])
    cocotb.log.info("first strobes: %s", strb_t[:6])
    cocotb.log.info("event log (name, t, tseg_cnt, rx_state, rx_bit_d):")
    for e in events[:26]:
        cocotb.log.info("   %s", e)

    assert sof_t, "sof_sync НИКОГДА не пульсировал"
    assert syn_t, "sync_edge до тайминга не доходит"
