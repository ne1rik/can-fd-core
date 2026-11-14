"""Classic frames with a dynamic stuff bit right after the 15th CRC bit."""
import os
import random
import cocotb
from cocotb.clock import Clock

from can_fd_reference import _raw_of, _crc_val, stuff_bits, dlc_len
from test_big_sweep import reset, run_case, IDS_BASE, IDS_EXT

EXT = int(os.environ.get("EXTENDED", "0")) == 1
CLS = int(os.environ.get("CLASSIC", "0")) == 1


def boundary_case(fid, dlc, data):
    raw = _raw_of(fid, dlc, data, False, EXT, True)
    crc = _crc_val(raw, 15, 0x4599, 0)
    cb = [(crc >> i) & 1 for i in range(14, -1, -1)]
    _st, pos = stuff_bits(raw + cb)
    return any(ri == len(raw) + 14 for ri, _si, _sb in pos)


@cocotb.test()
async def test_crc_boundary_stuff(dut):
    assert CLS, "build with CLASSIC=1"
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset(dut)

    ids = IDS_EXT if EXT else IDS_BASE
    found = []
    rng = random.Random(0xC0DEC)
    for _ in range(400000):
        dlc = rng.randrange(16)
        n = dlc_len(dlc, classic=True)
        style = rng.randrange(4)
        if style == 0:
            data = [0] * n
        elif style == 1:
            data = [0xFF] * n
        elif style == 2:
            data = [rng.choice([0x00, 0xFF]) for _ in range(n)]
        else:
            data = [rng.randrange(256) for _ in range(n)]
        fid = ids[rng.randrange(len(ids))]
        if boundary_case(fid, dlc, data):
            found.append((fid, dlc, data))
            if len(found) >= 40:
                break

    cocotb.log.info("ext=%d: %d CRC-boundary-stuff cases found", EXT, len(found))
    assert len(found) >= 30, f"only {len(found)} boundary cases; edge not exercised"

    failures = []
    for i, (fid, dlc, data) in enumerate(found):
        ok, why, ref, bus = await run_case(dut, fid, dlc, data, False)
        if not ok:
            tag = f"bnd{i} id={fid:#x} dlc={dlc}"
            cocotb.log.error("FAIL %s: %s", tag, why)
            cocotb.log.error("model: %s", "".join(map(str, ref)))
            cocotb.log.error("bus  : %s", "".join(map(str, bus)))
            failures.append(f"{tag}: {why}")
        await reset(dut)

    cocotb.log.info("crc-boundary ext=%d: %d cases, %d failures",
                    EXT, len(found), len(failures))
    assert not failures, f"{len(failures)} boundary failures"
