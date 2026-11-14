"""Real CTU reference vectors through the parameterized RTL loopback."""
import json
import os
from pathlib import Path

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge

from can_fd_reference import dlc_len
from test_big_sweep import reset, run_case

ROOT = Path(__file__).resolve().parent.parent
EXT = int(os.environ.get("EXTENDED", "0")) == 1
CLS = int(os.environ.get("CLASSIC", "0")) == 1

if CLS:
    FMT = "classic_ext" if EXT else "classic_base"
else:
    FMT = "fd_ext" if EXT else "fd_base"

VEC = ROOT / "coverage" / "ctu_vectors_all.json"
ALL = [v for v in json.loads(VEC.read_text()) if v.get("format") == FMT] if VEC.exists() else []

SHARD = int(os.environ.get("XVAL_SHARD", "0"))
SHARDS = int(os.environ.get("XVAL_SHARDS", "1"))
LIMIT = int(os.environ.get("XVAL_LIMIT", "0"))
SUB = ALL[:LIMIT] if LIMIT > 0 else ALL[SHARD::SHARDS]


@cocotb.test()
async def test_ctu_rtl(dut):
    assert VEC.exists(), "run scripts/xval_ctu_extract_all.py first"
    assert len(SUB) > 0, f"no vectors for {FMT} (total={len(ALL)})"

    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset(dut)

    failures = []
    passed = 0
    for idx, v in enumerate(SUB):
        fid, dlc = v["id"], v["dlc"]
        brs = False if CLS else bool(v["brs"])
        n = dlc_len(dlc, classic=CLS)
        data = (v["data"] + [0] * n)[:n]
        ok, why, ref, bus = await run_case(dut, fid, dlc, data, brs)
        if ok:
            passed += 1
        else:
            tag = f"{FMT}[{idx}] id={fid:#x} dlc={dlc} brs={int(brs)}"
            failures.append(f"{tag}: {why}")
            if len(failures) <= 5:
                cocotb.log.error("%s -> %s", tag, why)
                cocotb.log.error("model: %s", "".join(map(str, ref)))
                cocotb.log.error("bus  : %s", "".join(map(str, bus)))
            if len(failures) >= 15:
                break
        if (idx + 1) % 300 == 0:
            cocotb.log.info("%s: %d/%d, failures=%d", FMT, idx + 1, len(SUB), len(failures))
        await reset(dut)

    cocotb.log.info("%s: PASS %d/%d (shard=%d/%d limit=%d), failures=%d",
                    FMT, passed, len(SUB), SHARD, SHARDS, LIMIT, len(failures))
    assert not failures, f"{len(failures)} {FMT} vectors failed"
