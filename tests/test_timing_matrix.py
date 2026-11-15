"""Real-timing matrix. RX outputs are latched on the rx_done cycle.

rx_valid/rx_done are single-strobe pulses; reading them after any extra
wait yields stale zeros. Everything is captured at the done cycle.
"""
import os
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer
from can_fd_reference import generate_can_fd_frame, dlc_len

EXT = int(os.environ.get("EXTENDED", "0")) == 1
CLS = int(os.environ.get("CLASSIC", "0")) == 1
NBT = (1 + int(os.environ.get("NBT_TSEG1", "0")) + int(os.environ.get("NBT_TSEG2", "0"))) \
      * int(os.environ.get("NBT_PRESCALER", "1"))
DBT = (1 + int(os.environ.get("DBT_TSEG1", "0")) + int(os.environ.get("DBT_TSEG2", "0"))) \
      * int(os.environ.get("DBT_PRESCALER", "1"))


async def wait_tx_idle(dut, limit=40000):
    for _ in range(limit):
        if int(dut.tx_busy.value) == 0:
            return True
        await RisingEdge(dut.clk)
    return False


async def one_frame(dut, fid, dlc, brs, data):
    n = dlc_len(dlc, classic=CLS)
    data = data[:n]
    ref = generate_can_fd_frame(fid, dlc, data, brs, extended=EXT, classic=CLS)
    tag = f"dlc={dlc} brs={int(brs)}"

    if not await wait_tx_idle(dut):
        return f"{tag}: TX never idle before start"

    bus = []

    async def cap():
        while True:
            await RisingEdge(dut.clk)
            await Timer(1, unit="ns")
            if int(dut.tx_bit_valid.value) == 1:
                bus.append(int(dut.tx_bit.value))

    c = cocotb.start_soon(cap())
    dut.tx_id.value = fid
    dut.tx_dlc.value = dlc
    dut.tx_brs.value = int(brs)
    dut.tx_data.value = (int.from_bytes(bytes(data), "big") << (512 - 8 * n)) if n else 0
    dut.tx_start.value = 1
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")
    dut.tx_start.value = 0

    snap = None
    for _ in range(len(ref) * max(NBT, DBT) * 4 + 20000):
        await RisingEdge(dut.clk)
        await Timer(1, unit="ns")
        if int(dut.rx_done.value) == 1:
            snap = (int(dut.rx_valid.value),
                    int(dut.rx_crc_err.value),
                    int(dut.rx_stuff_err.value),
                    int(dut.rx_id.value),
                    int(dut.rx_dlc.value),
                    int(dut.rx_data.value))
            break
    c.cancel()

    await wait_tx_idle(dut)
    for _ in range(120):
        await RisingEdge(dut.clk)

    if snap is None:
        return f"{tag}: TIMEOUT bus={len(bus)}/{len(ref)}"

    valid, crc, stuff, rid, rdlc, rdata = snap

    if len(bus) != len(ref):
        return f"{tag}: LEN {len(bus)} != {len(ref)}"
    ack = len(ref) - 9
    diffs = [i for i in range(len(ref)) if bus[i] != ref[i] and i != ack]
    if diffs:
        return f"{tag}: {len(diffs)} DIFFS first={diffs[0]}"
    if valid != 1:
        return f"{tag}: REJECTED crc={crc} stuff={stuff}"
    if rid != fid or rdlc != dlc:
        return f"{tag}: FIELD id={rid:#x}/{fid:#x} dlc={rdlc}/{dlc}"
    for k in range(n):
        got = (rdata >> (512 - 8 * (k + 1))) & 0xFF
        if got != data[k]:
            return f"{tag}: DATA byte{k} {got:#04x}!={data[k]:#04x}"
    return None


@cocotb.test()
async def test_timing_matrix(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    dut.rst_n.value = 0
    dut.tx_start.value = 0
    dut.tx_data.value = 0
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)

    cocotb.log.info("config: ext=%d cls=%d NBT=%d clk/bit DBT=%d clk/bit", EXT, CLS, NBT, DBT)

    dlcs = [0, 4, 8, 12, 15] if not CLS else [0, 4, 8]
    brs_modes = [False] if CLS else [False, True]
    pats = [[0x00] * 64, [0xFF] * 64, [0xAA if i % 2 == 0 else 0x55 for i in range(64)]]

    fails, total = [], 0
    for dlc in dlcs:
        for brs in brs_modes:
            for pi, pat in enumerate(pats):
                total += 1
                err = await one_frame(dut, 0x1127B78 if EXT else 0x16b, dlc, brs, pat)
                if err:
                    fails.append(f"pat{pi} {err}")

    cocotb.log.info("matrix: %d cases, %d failures", total, len(fails))
    for f in fails[:12]:
        cocotb.log.error("  %s", f)
    assert not fails, f"{len(fails)}/{total} real-timing cases failed"
