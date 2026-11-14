"""Real two-phase timing smoke test with diagnostics.

Runs one frame with nonzero TSEG and reports whether the round-trip works,
plus strobe activity inside TX/RX, to localise a stall.
"""
import os
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer
from can_fd_reference import generate_can_fd_frame, dlc_len

EXT = int(os.environ.get("EXTENDED", "0")) == 1
CLS = int(os.environ.get("CLASSIC", "0")) == 1
NBT = 1 + int(os.environ.get("NBT_TSEG1", "0")) + int(os.environ.get("NBT_TSEG2", "0"))
DBT = 1 + int(os.environ.get("DBT_TSEG1", "0")) + int(os.environ.get("DBT_TSEG2", "0"))


def probe(dut, path):
    cur = dut
    for part in path.split("."):
        try:
            cur = getattr(cur, part)
        except AttributeError:
            return None
    return cur


@cocotb.test()
async def test_timing_real_one_frame(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    dut.rst_n.value = 0
    dut.tx_start.value = 0
    dut.tx_data.value = 0
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)

    fid = 0x16b
    dlc = 4
    brs = False if CLS else bool(int(os.environ.get("DBG_BRS", "0")))
    n = dlc_len(dlc, classic=CLS)
    data = [0x11, 0x22, 0x33, 0x44][:n]
    ref = generate_can_fd_frame(fid, dlc, data, brs, extended=EXT, classic=CLS)

    cocotb.log.info("timing: NBT=%d clocks/bit, DBT=%d clocks/bit, model len=%d",
                    NBT, DBT, len(ref))

    bus = []
    rx_sample_hits = 0
    tx_boundary_hits = 0
    rx_state_seen = set()

    rx_strobe = probe(dut, "u_rx.rx_sample_strobe")
    tx_bnd    = probe(dut, "u_tx.bt_bit_boundary")
    rx_state  = probe(dut, "u_rx.state")

    async def monitor():
        nonlocal rx_sample_hits, tx_boundary_hits
        while True:
            await RisingEdge(dut.clk)
            await Timer(1, unit="ns")
            if int(dut.tx_bit_valid.value) == 1:
                bus.append(int(dut.tx_bit.value))
            if rx_strobe is not None and int(rx_strobe.value) == 1:
                rx_sample_hits += 1
            if tx_bnd is not None and int(tx_bnd.value) == 1:
                tx_boundary_hits += 1
            if rx_state is not None:
                rx_state_seen.add(int(rx_state.value))

    mon = cocotb.start_soon(monitor())

    dut.tx_id.value = fid
    dut.tx_dlc.value = dlc
    dut.tx_brs.value = int(brs)
    dut.tx_data.value = (int.from_bytes(bytes(data), "big") << (512 - 8 * n)) if n else 0
    dut.tx_start.value = 1
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")
    dut.tx_start.value = 0

    budget = len(ref) * max(NBT, DBT) * 4 + 40000
    done = False
    for _ in range(budget):
        await RisingEdge(dut.clk)
        await Timer(1, unit="ns")
        if int(dut.rx_done.value) == 1:
            done = True
            break
    mon.cancel()

    cocotb.log.info("bus bits=%d (model %d), rx_done=%d", len(bus), len(ref), done)
    cocotb.log.info("tx bit_boundary pulses=%d, rx sample strobes=%d",
                    tx_boundary_hits, rx_sample_hits)
    cocotb.log.info("rx states visited=%s", sorted(rx_state_seen))
    cocotb.log.info("RX crc=%d stuff=%d valid=%d",
                    int(dut.rx_crc_err.value), int(dut.rx_stuff_err.value),
                    int(dut.rx_valid.value))
    if bus:
        cocotb.log.info("bus head: %s", "".join(map(str, bus[:60])))
    cocotb.log.info("mod head: %s", "".join(map(str, ref[:60])))

    assert done, "timeout: rx_done never asserted (real-timing stall)"
    assert len(bus) == len(ref), f"bus length {len(bus)} != model {len(ref)}"
    ack = len(ref) - 9
    diffs = [i for i in range(len(ref)) if bus[i] != ref[i] and i != ack]
    assert not diffs, f"{len(diffs)} bit diffs, first={diffs[0]}"
    assert int(dut.rx_valid.value) == 1, "RX rejected the frame"
