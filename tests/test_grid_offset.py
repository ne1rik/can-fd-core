"""Numeric: TX bit-emit times vs RX sample-strobe times, first 24 events."""
import os
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer
from cocotb.utils import get_sim_time
from can_fd_reference import generate_can_fd_frame, dlc_len

EXT = int(os.environ.get("EXTENDED", "0")) == 1


def h(dut, path):
    cur = dut
    for part in path.split("."):
        if not hasattr(cur, part):
            raise AssertionError(f"MISSING HANDLE {path}")
        cur = getattr(cur, part)
    return cur


@cocotb.test()
async def test_grid_offset(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    dut.rst_n.value = 0
    dut.tx_start.value = 0
    dut.tx_data.value = 0
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)

    tx_state = h(dut, "u_tx.state")
    rx_strb  = h(dut, "u_rx.rx_sample_strobe")
    rx_state = h(dut, "u_rx.state")
    rx_raw   = h(dut, "u_rx.raw_idx")
    rx_cnt   = h(dut, "u_rx.u_timing.tseg_cnt")

    fid, dlc = 0x16b, 8
    data = [0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88]
    n = dlc_len(dlc, classic=False)
    ref = generate_can_fd_frame(fid, dlc, data, True, extended=EXT, classic=False)

    tx_t, rx_t = [], []

    async def mon():
        while True:
            await RisingEdge(dut.clk)
            await Timer(1, unit="ns")
            t = get_sim_time(unit="ns")
            if int(dut.tx_bit_valid.value) == 1 and len(tx_t) < 24:
                tx_t.append(t)
            if int(rx_strb.value) == 1 and int(rx_state.value) != 0 and len(rx_t) < 24:
                rx_t.append((t, int(rx_raw.value), int(rx_cnt.value)))

    m = cocotb.start_soon(mon())
    dut.tx_id.value = fid
    dut.tx_dlc.value = dlc
    dut.tx_brs.value = 1
    dut.tx_data.value = int.from_bytes(bytes(data), "big") << (512 - 8 * n)
    dut.tx_start.value = 1
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")
    dut.tx_start.value = 0

    for _ in range(len(ref) * 70 + 40000):
        await RisingEdge(dut.clk)
        await Timer(1, unit="ns")
        if int(dut.rx_done.value) == 1:
            break
    m.cancel()

    cocotb.log.info("TX emit times[:20] = %s", tx_t[:20])
    cocotb.log.info("TX emit deltas[:19] = %s",
                    [tx_t[i+1]-tx_t[i] for i in range(min(19, len(tx_t)-1))])
    cocotb.log.info("RX strobes (t, raw_idx, tseg_cnt)[:20] = %s", rx_t[:20])
    if tx_t and rx_t:
        cocotb.log.info("SOF: TX emit=%.1f ns, RX first strobe=%.1f ns, offset=%.1f ns (%.1f clocks)",
                        tx_t[0], rx_t[0][0], rx_t[0][0]-tx_t[0], (rx_t[0][0]-tx_t[0])/10)
    assert tx_t, "TX never emitted"
    assert rx_t, "RX never sampled"
