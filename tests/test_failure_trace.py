"""Trace one failing case: dlc=4 brs=0 in base_17/5"""
import os
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
                raise AssertionError(f"MISSING HANDLE {path}")
            cocotb.log.warning("MISSING HANDLE: %s", path)
            return None
        cur = getattr(cur, part)
    return cur


@cocotb.test()
async def test_failure_trace(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    dut.rst_n.value = 0
    dut.tx_start.value = 0
    dut.tx_data.value = 0
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)

    rx_st = h(dut, "u_rx.state")
    rx_dn = h(dut, "u_rx.rx_done")
    rx_stb = h(dut, "u_rx.rx_sample_strobe")
    tx_st = h(dut, "u_tx.state")
    tx_bnd = h(dut, "u_tx.bt_bit_boundary")

    fid, dlc = 0x16b, 4
    data = [0xFF] * 4
    n = dlc_len(dlc, classic=False)
    ref = generate_can_fd_frame(fid, dlc, data, False, extended=False, classic=False)
    cocotb.log.info("model len=%d", len(ref))

    bus = []
    rx_states = []
    rx_done_t = None
    last_strobe_t = None

    async def mon():
        nonlocal rx_done_t, last_strobe_t
        while True:
            await RisingEdge(dut.clk)
            await Timer(1, unit="ns")
            t = get_sim_time(unit="ns")
            if int(dut.tx_bit_valid.value) == 1:
                bus.append(int(dut.tx_bit.value))
            if int(rx_stb.value) == 1:
                last_strobe_t = t
                rx_states.append((t, int(rx_st.value)))
            if int(rx_dn.value) == 1:
                rx_done_t = t

    m = cocotb.start_soon(mon())

    dut.tx_id.value = fid
    dut.tx_dlc.value = dlc
    dut.tx_brs.value = 0
    dut.tx_data.value = int.from_bytes(bytes(data), "big") << (512 - 8 * n)
    dut.tx_start.value = 1
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")
    dut.tx_start.value = 0

    for _ in range(len(ref) * 80 + 20000):
        await RisingEdge(dut.clk)
        await Timer(1, unit="ns")
        if rx_done_t is not None:
            break
    m.cancel()

    cocotb.log.info("bus=%d/%d rx_done@%s last_strobe@%s",
                    len(bus), len(ref), rx_done_t, last_strobe_t)
    cocotb.log.info("rx_states[:12]: %s", rx_states[:12])
    cocotb.log.info("rx_states[-12:]: %s", rx_states[-12:])

    if rx_done_t is None:
        cocotb.log.error("TIMEOUT: rx_done never asserted")
    else:
        cocotb.log.info("rx_done at %s ns, valid=%d crc=%d",
                        rx_done_t, int(dut.rx_valid.value), int(dut.rx_crc_err.value))
