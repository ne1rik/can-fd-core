"""Per-frame start state: is TX out of data phase, is RX back in IDLE?"""
import os
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer
from can_fd_reference import generate_can_fd_frame, dlc_len

EXT = int(os.environ.get("EXTENDED", "0")) == 1
CLS = int(os.environ.get("CLASSIC", "0")) == 1
DLC = int(os.environ.get("DBG_DLC", "4"))
BRS = False if CLS else bool(int(os.environ.get("DBG_BRS", "0")))


def h(dut, path):
    cur = dut
    for part in path.split("."):
        if not hasattr(cur, part):
            raise AssertionError(f"MISSING HANDLE {path}")
        cur = getattr(cur, part)
    return cur


@cocotb.test()
async def test_multiframe_probe(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    dut.rst_n.value = 0
    dut.tx_start.value = 0
    dut.tx_data.value = 0
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)

    tx_st = h(dut, "u_tx.state")
    tx_ph = h(dut, "u_tx.brs_active_reg")
    rx_st = h(dut, "u_rx.state")
    rx_ph = h(dut, "u_rx.brs_phase_r")

    fid = 0x1127B78 if EXT else 0x16b
    n = dlc_len(DLC, classic=CLS)
    data = [(0x11 * (i + 1)) & 0xFF for i in range(n)]
    ref = generate_can_fd_frame(fid, DLC, data, BRS, extended=EXT, classic=CLS)
    cocotb.log.info("frame len=%d dlc=%d brs=%d cls=%d", len(ref), DLC, int(BRS), int(CLS))

    bad = 0
    for idx in range(5):
        for _ in range(40000):
            if int(dut.tx_busy.value) == 0:
                break
            await RisingEdge(dut.clk)
        for _ in range(150):
            await RisingEdge(dut.clk)

        cocotb.log.info("frame %d START: tx_state=%d tx_data_phase=%d rx_state=%d rx_data_phase=%d",
                        idx, int(tx_st.value), int(tx_ph.value),
                        int(rx_st.value), int(rx_ph.value))
        if int(rx_st.value) != 0 or int(tx_ph.value) != 0:
            bad += 1

        cnt = [0]

        async def cap():
            while True:
                await RisingEdge(dut.clk)
                await Timer(1, unit="ns")
                if int(dut.tx_bit_valid.value) == 1:
                    cnt[0] += 1

        c = cocotb.start_soon(cap())
        dut.tx_id.value = fid
        dut.tx_dlc.value = DLC
        dut.tx_brs.value = int(BRS)
        dut.tx_data.value = (int.from_bytes(bytes(data), "big") << (512 - 8 * n)) if n else 0
        dut.tx_start.value = 1
        await RisingEdge(dut.clk)
        await Timer(1, unit="ns")
        dut.tx_start.value = 0

        snap = None
        for _ in range(len(ref) * 80 + 20000):
            await RisingEdge(dut.clk)
            await Timer(1, unit="ns")
            if int(dut.rx_done.value) == 1:
                snap = (int(dut.rx_valid.value), int(dut.rx_crc_err.value),
                        int(dut.rx_stuff_err.value), cnt[0])
                break
        c.cancel()
        if snap is None:
            cocotb.log.error("frame %d: TIMEOUT bus=%d/%d", idx, cnt[0], len(ref))
            bad += 1
        else:
            v, cr, st, nb = snap
            cocotb.log.info("frame %d DONE: valid=%d crc=%d stuff=%d bus=%d/%d",
                            idx, v, cr, st, nb, len(ref))
            if v != 1 or nb != len(ref):
                bad += 1

    cocotb.log.info("bad frames/states: %d", bad)
    assert bad == 0, f"{bad} anomalies across 5 frames"
