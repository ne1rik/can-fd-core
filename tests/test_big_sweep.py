"""1264 cases per Classic format, 1344 per FD format. CASE_IDX=N dumps one case."""
import os
import random
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer
from can_fd_reference import generate_can_fd_frame, dlc_len

EXT = int(os.environ.get("EXTENDED", "0")) == 1
CLS = int(os.environ.get("CLASSIC", "0")) == 1

IDS_BASE = [0, 1, 0x16b, 0x7FF]
IDS_EXT = [0, 1, 0x1127B78, 0x1FFFFFFF, 0x15555555]
SEEDS = [1234, 0xBEEF, 0xC0FFEE, 0x5EED, 7, 99, 0xA11CE, 0xD1CE, 0x516B, 0x2026] \
        + list(range(1000, 1064))
PATTERNS = ["zeros", "ones", "alt", "alt_inv", "ramp"]


async def reset(dut):
    dut.rst_n.value = 0
    dut.tx_start.value = 0
    dut.tx_data.value = 0
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)


def make_data(p, n, rng):
    if p == "zeros":
        return [0] * n
    if p == "ones":
        return [0xFF] * n
    if p == "alt":
        return [0xAA if i % 2 == 0 else 0x55 for i in range(n)]
    if p == "alt_inv":
        return [0x55 if i % 2 == 0 else 0xAA for i in range(n)]
    if p == "ramp":
        return [i & 0xFF for i in range(n)]
    return [rng.randrange(256) for _ in range(n)]


def build_cases():
    ids = IDS_EXT if EXT else IDS_BASE
    cases = []
    for d in range(16):
        n = dlc_len(d, classic=CLS)
        for pi, p in enumerate(PATTERNS):
            data = make_data(p, n, None)
            if CLS:
                cases.append((ids[(d + pi) % len(ids)], d, data, False))
            else:
                cases.append((ids[(d + pi) % len(ids)], d, data, False))
                cases.append((ids[(d + pi + 1) % len(ids)], d, data, True))
    for d in range(16):
        n = dlc_len(d, classic=CLS)
        for s in SEEDS:
            rng = random.Random(s * 1000 + d)
            data = [rng.randrange(256) for _ in range(n)]
            brs = False if CLS else bool(rng.randrange(2))
            cases.append((ids[rng.randrange(len(ids))], d, data, brs))
    return cases


async def run_case(dut, fid, dlc, data, brs):
    n = dlc_len(dlc, classic=CLS)
    ref = generate_can_fd_frame(fid, dlc, data, brs, extended=EXT, classic=CLS)
    bus = []

    async def capture():
        while True:
            await RisingEdge(dut.clk)
            await Timer(1, unit="ns")
            if int(dut.tx_bit_valid.value) == 1:
                bus.append(int(dut.tx_bit.value))

    cap = cocotb.start_soon(capture())
    dut.tx_id.value = fid
    dut.tx_dlc.value = dlc
    dut.tx_brs.value = int(brs)
    dut.tx_data.value = (int.from_bytes(bytes(data), "big") << (512 - 8 * n)) if n else 0
    dut.tx_start.value = 1
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")
    dut.tx_start.value = 0

    done = False
    for _ in range(len(ref) * 6 + 6000):
        await RisingEdge(dut.clk)
        await Timer(1, unit="ns")
        if int(dut.rx_done.value) == 1:
            done = True
            break
    cap.cancel()

    if not done:
        return False, "timeout", ref, bus
    if len(bus) != len(ref):
        return False, f"len {len(bus)} != {len(ref)}", ref, bus
    ack = len(ref) - 9
    diffs = [i for i in range(len(ref)) if bus[i] != ref[i] and i != ack]
    if diffs:
        return False, f"{len(diffs)} bit diffs, first={diffs[0]}", ref, bus
    if bus[ack] != 0:
        return False, "ACK not dominant", ref, bus
    if not int(dut.rx_valid.value):
        return False, (f"rx invalid crc={int(dut.rx_crc_err.value)} "
                       f"stuff={int(dut.rx_stuff_err.value)}"), ref, bus
    if int(dut.rx_id.value) != fid:
        return False, f"id {int(dut.rx_id.value):#x}", ref, bus
    if int(dut.rx_dlc.value) != dlc:
        return False, f"dlc {int(dut.rx_dlc.value)}", ref, bus
    rx = int(dut.rx_data.value)
    for k in range(n):
        got = (rx >> (512 - 8 * (k + 1))) & 0xFF
        if got != data[k]:
            return False, f"byte{k} {got:#04x}!={data[k]:#04x}", ref, bus
    return True, "ok", ref, bus


@cocotb.test()
async def test_big_sweep(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset(dut)

    cases = build_cases()
    expected = 1264 if CLS else 1344
    assert len(cases) == expected, f"case count {len(cases)} != {expected}"

    single = os.environ.get("CASE_IDX")
    single = single if single else None
    idx_list = [int(single)] if single is not None else range(len(cases))

    failures = []
    for idx in idx_list:
        fid, dlc, data, brs = cases[idx]
        ok, why, ref, bus = await run_case(dut, fid, dlc, data, brs)
        tag = f"case{idx} id={fid:#x} dlc={dlc} brs={int(brs)}"
        if single is not None:
            cocotb.log.info("model len=%d: %s", len(ref), "".join(map(str, ref)))
            cocotb.log.info("bus   len=%d: %s", len(bus), "".join(map(str, bus)))
        if not ok:
            cocotb.log.error("FAIL %s: %s", tag, why)
            failures.append(f"{tag}: {why}")
            if len(failures) >= 20 and single is None:
                break
        if single is None:
            await reset(dut)

    cocotb.log.info("ext=%d cls=%d: %d cases, %d failures",
                    EXT, CLS, len(idx_list), len(failures))
    for f in failures:
        cocotb.log.error("  %s", f)
    assert not failures, f"{len(failures)} failures"
