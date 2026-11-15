"""Localise TX/RX phase desync. No silent except: missing handles are loud."""
import os
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer
from cocotb.utils import get_sim_time
from can_fd_reference import generate_can_fd_frame, frame_layout, dlc_len

EXT = int(os.environ.get("EXTENDED", "0")) == 1


def handle(dut, path, required=True):
    cur = dut
    for part in path.split("."):
        if not hasattr(cur, part):
            msg = f"MISSING HANDLE: {path} (нет '{part}')"
            if required:
                raise AssertionError(msg)
            cocotb.log.warning(msg)
            return None
        cur = getattr(cur, part)
    cocotb.log.info("handle ok: %s", path)
    return cur


@cocotb.test()
async def test_brs_phase_trace(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    dut.rst_n.value = 0
    dut.tx_start.value = 0
    dut.tx_data.value = 0
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)

    h_tx_phase = handle(dut, "u_tx.bt_phase")
    h_tx_brs   = handle(dut, "u_tx.brs_active_reg")
    h_tx_wridx = handle(dut, "u_tx.brs_wr_idx")
    h_tx_rd    = handle(dut, "u_tx.rd_idx")
    h_rx_phase = handle(dut, "u_rx.bt_phase")
    h_rx_brs   = handle(dut, "u_rx.brs_seen")
    h_rx_raw   = handle(dut, "u_rx.raw_idx")
    h_rx_strb  = handle(dut, "u_rx.rx_sample_strobe")

    fid, dlc = 0x16b, 8
    data = [0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88]
    n = dlc_len(dlc, classic=False)
    ref = generate_can_fd_frame(fid, dlc, data, True, extended=EXT, classic=False)
    lo = frame_layout(fid, dlc, data, True, extended=EXT, classic=False)
    cocotb.log.info("MODEL brs_index=%d, model len=%d", lo["brs_index"], len(ref))

    bus = []
    tx_sw, rx_sw = [], []
    rx_strobes = 0

    async def monitor():
        nonlocal rx_strobes
        tp_prev, rp_prev = int(h_tx_phase.value), int(h_rx_phase.value)
        while True:
            await RisingEdge(dut.clk)
            await Timer(1, unit="ns")
            t = get_sim_time(unit="ns")
            if int(dut.tx_bit_valid.value) == 1:
                bus.append(int(dut.tx_bit.value))
            if int(h_rx_strb.value) == 1:
                rx_strobes += 1
            tp, rp = int(h_tx_phase.value), int(h_rx_phase.value)
            if tp != tp_prev:
                tx_sw.append((t, len(bus), tp, int(h_tx_rd.value), int(h_tx_wridx.value)))
                cocotb.log.info("TX phase %d->%d @%sns bus_bit=%d rd_idx=%d brs_wr_idx=%d",
                                tp_prev, tp, t, len(bus), int(h_tx_rd.value), int(h_tx_wridx.value))
                tp_prev = tp
            if rp != rp_prev:
                rx_sw.append((t, rx_strobes, rp, int(h_rx_raw.value)))
                cocotb.log.info("RX phase %d->%d @%sns rx_strobe=%d raw_idx=%d brs_seen=%d",
                                rp_prev, rp, t, rx_strobes, int(h_rx_raw.value), int(h_rx_brs.value))
                rp_prev = rp

    mon = cocotb.start_soon(monitor())

    dut.tx_id.value = fid
    dut.tx_dlc.value = dlc
    dut.tx_brs.value = 1
    dut.tx_data.value = int.from_bytes(bytes(data), "big") << (512 - 8 * n)
    dut.tx_start.value = 1
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")
    dut.tx_start.value = 0

    done = False
    for _ in range(len(ref) * 17 * 4 + 40000):
        await RisingEdge(dut.clk)
        await Timer(1, unit="ns")
        if int(dut.rx_done.value) == 1:
            done = True
            break
    mon.cancel()

    cocotb.log.info("bus=%d model=%d done=%d crc=%d stuff=%d valid=%d",
                    len(bus), len(ref), done, int(dut.rx_crc_err.value),
                    int(dut.rx_stuff_err.value), int(dut.rx_valid.value))
    cocotb.log.info("TX switches: %s", tx_sw)
    cocotb.log.info("RX switches: %s", rx_sw)

    ack = len(ref) - 9
    diffs = [i for i in range(min(len(bus), len(ref))) if bus[i] != ref[i] and i != ack]
    cocotb.log.info("first 12 bus diffs vs model: %s", diffs[:12])
    if diffs:
        i = diffs[0]
        cocotb.log.info("at %d: model=%s", i, "".join(map(str, ref[max(0,i-6):i+10])))
        cocotb.log.info("at %d: bus  =%s", i, "".join(map(str, bus[max(0,i-6):i+10])))

    assert tx_sw, "TX никогда не переключил фазу"
    assert rx_sw, "RX никогда не переключил фазу"
