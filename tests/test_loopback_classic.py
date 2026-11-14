"""Classic CAN loopback against CTU reference vectors.

Requires a DUT built with CLASSIC=1.
EXTENDED selects classic_base vs classic_ext vector set.
Set XVAL_LIMIT=N for quick debug runs (no sharding).
"""
import json
import os
from pathlib import Path

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer

from can_fd_reference import generate_can_fd_frame, dlc_len

ROOT = Path(__file__).resolve().parent.parent
VEC_PATH = ROOT / "coverage" / "ctu_vectors_all.json"

assert VEC_PATH.exists(), "coverage/ctu_vectors_all.json missing; run scripts/xval_ctu_extract_all.py"
ALL = json.loads(VEC_PATH.read_text())

EXT = int(os.environ.get("EXTENDED", "0")) == 1
CLS = int(os.environ.get("CLASSIC", "0")) == 1
FORMAT = "classic_ext" if EXT else "classic_base"

VECTORS = [v for v in ALL if v.get("format") == FORMAT]

SHARD = int(os.environ.get("XVAL_SHARD", "0"))
SHARDS = int(os.environ.get("XVAL_SHARDS", "1"))
LIMIT = int(os.environ.get("XVAL_LIMIT", "0"))

if LIMIT > 0:
    SUBSET = VECTORS[:LIMIT]
else:
    SUBSET = VECTORS[SHARD::SHARDS]

assert len(SUBSET) > 0, (
    f"No {FORMAT} vectors found (total classic={len(VECTORS)}). "
    "Check extractor and format filter."
)


async def _reset(dut):
    dut.rst_n.value = 0
    dut.tx_start.value = 0
    dut.tx_data.value = 0
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)


@cocotb.test()
async def test_classic_loopback_ctu_vectors(dut):
    """Classic CAN frames must round-trip through the parameterized RTL."""
    assert CLS, "This test requires DUT built with CLASSIC=1"

    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await _reset(dut)

    failures = []
    passed = 0

    for idx, v in enumerate(SUBSET):
        fid = v["id"]
        dlc = v["dlc"]
        n = dlc_len(dlc, classic=True)
        data = (v["data"] + [0] * n)[:n]
        ext = EXT

        ref_bits = generate_can_fd_frame(fid, dlc, data, False, extended=ext, classic=True)

        dut.tx_id.value = fid
        dut.tx_dlc.value = dlc
        dut.tx_brs.value = 0
        dut.tx_data.value = (int.from_bytes(bytes(data), "big") << (512 - 8 * n)) if n else 0

        dut.tx_start.value = 1
        await RisingEdge(dut.clk)
        await Timer(1, unit="ns")
        dut.tx_start.value = 0

        done = False
        for _ in range(len(ref_bits) * 4 + 4000):
            await RisingEdge(dut.clk)
            await Timer(1, unit="ns")
            if int(dut.rx_done.value) == 1:
                done = True
                break

        tag = f"{FORMAT}[{idx}] id={fid:#x} dlc={dlc}"

        if not done:
            failures.append(f"{tag}: rx_done timeout")
            if len(failures) >= 10:
                break
            continue

        if int(dut.rx_crc_err.value) or int(dut.rx_stuff_err.value) or not int(dut.rx_valid.value):
            failures.append(
                f"{tag}: verdict invalid crc={int(dut.rx_crc_err.value)} "
                f"stuff={int(dut.rx_stuff_err.value)} valid={int(dut.rx_valid.value)}"
            )
            if len(failures) >= 10:
                break
            continue

        if int(dut.rx_id.value) != fid:
            failures.append(f"{tag}: ID {int(dut.rx_id.value):#x} != {fid:#x}")
            if len(failures) >= 10:
                break
            continue

        if int(dut.rx_dlc.value) != dlc:
            failures.append(f"{tag}: DLC {int(dut.rx_dlc.value)} != {dlc}")
            if len(failures) >= 10:
                break
            continue

        rx = int(dut.rx_data.value)
        mismatch = None
        for k in range(n):
            got = (rx >> (512 - 8 * (k + 1))) & 0xFF
            if got != data[k]:
                mismatch = f"byte{k} {got:#04x}!={data[k]:#04x}"
                break

        if mismatch:
            failures.append(f"{tag}: data {mismatch}")
            if len(failures) >= 10:
                break
            continue

        passed += 1
        if (idx + 1) % 200 == 0:
            cocotb.log.info("classic loopback: %d/%d, failures=%d",
                            idx + 1, len(SUBSET), len(failures))

    cocotb.log.info("%s shard=%d/%d limit=%d: PASS %d/%d, failures=%d",
                    FORMAT, SHARD, SHARDS, LIMIT, passed, len(SUBSET), len(failures))

    for f in failures[:20]:
        cocotb.log.error("  %s", f)

    assert not failures, f"{len(failures)} {FORMAT} vectors failed"
