"""Cross-validation: CTU reference frame metadata through our TX -> RX.

Compares five aspects per vector: ID, DLC, data bytes, BRS (observed on the
wire at the model-predicted index), and receiver verdict. The CTU `seq`
waveform is deliberately NOT compared here: it is a timed bus trace at
500k/2M with an 80% sample point, a different abstraction level.

Shard with XVAL_SHARD / XVAL_SHARDS to keep runs short.
"""
import json
import os
from pathlib import Path

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer

from can_fd_reference import generate_can_fd_frame, frame_layout, dlc_len

ROOT = Path(__file__).resolve().parent.parent
VECTORS = json.loads((ROOT / "coverage" / "ctu_vectors.json").read_text())
SHARD = int(os.environ.get("XVAL_SHARD", "0"))
SHARDS = int(os.environ.get("XVAL_SHARDS", "1"))
SUBSET = VECTORS[SHARD::SHARDS]


async def _reset(dut):
    dut.rst_n.value = 0
    dut.tx_start.value = 0
    dut.tx_data.value = 0
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)


async def _capture(dut, sink):
    """Record bus bits while tx_bit_valid is high."""
    while True:
        await RisingEdge(dut.clk)
        await Timer(1, unit="ns")
        if int(dut.tx_bit_valid.value) == 1:
            sink.append(int(dut.tx_bit.value))


@cocotb.test()
async def test_ctu_vectors_loopback(dut):
    """Every in-scope CTU vector must round-trip with all five aspects intact."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await _reset(dut)

    have_bus = hasattr(dut, "tx_bit_valid") and hasattr(dut, "tx_bit")
    failures = []
    passed = 0

    for idx, v in enumerate(SUBSET):
        fid, dlc, brs = v["id"], v["dlc"], bool(v["brs"])
        n = dlc_len(dlc)
        data = (v["data"] + [0] * n)[:n]
        ref = generate_can_fd_frame(fid, dlc, data, brs)
        lay = frame_layout(fid, dlc, data, brs)
        tag = f"vec{SHARD + idx * SHARDS} id={fid:#05x} dlc={dlc} brs={int(brs)}"

        bus = []
        cap = cocotb.start_soon(_capture(dut, bus)) if have_bus else None

        dut.tx_id.value = fid
        dut.tx_dlc.value = dlc
        dut.tx_brs.value = 1 if brs else 0
        dut.tx_data.value = (int.from_bytes(bytes(data), "big") << (512 - 8 * n)) if n else 0

        dut.tx_start.value = 1
        await RisingEdge(dut.clk)
        await Timer(1, unit="ns")
        dut.tx_start.value = 0

        done = False
        for _ in range(len(ref) * 3 + 2000):
            await RisingEdge(dut.clk)
            await Timer(1, unit="ns")
            if int(dut.rx_done.value) == 1:
                done = True
                break

        if cap:
            cap.cancel()

        if not done:
            failures.append(f"{tag}: rx_done timeout"); continue

        # aspect 5: verdict
        if int(dut.rx_crc_err.value) or int(dut.rx_stuff_err.value) or not int(dut.rx_valid.value):
            failures.append(f"{tag}: verdict crc={int(dut.rx_crc_err.value)} "
                            f"stuff={int(dut.rx_stuff_err.value)} "
                            f"valid={int(dut.rx_valid.value)}")
            continue
        # aspects 1-2
        if int(dut.rx_id.value) != fid:
            failures.append(f"{tag}: ID {int(dut.rx_id.value):#x}"); continue
        if int(dut.rx_dlc.value) != dlc:
            failures.append(f"{tag}: DLC {int(dut.rx_dlc.value)}"); continue
        # aspect 3
        rx = int(dut.rx_data.value)
        mismatch = None
        for k in range(n):
            got = (rx >> (512 - 8 * (k + 1))) & 0xFF
            if got != data[k]:
                mismatch = f"byte{k} {got:#04x}!={data[k]:#04x}"
                break
        if mismatch:
            failures.append(f"{tag}: data {mismatch}"); continue
        # aspect 4: BRS as seen on the wire
        if have_bus:
            if len(bus) != len(ref):
                failures.append(f"{tag}: bus len {len(bus)} != {len(ref)}"); continue
            if bus[lay["brs_index"]] != int(brs):
                failures.append(f"{tag}: BRS wire {bus[lay['brs_index']]}"); continue

        passed += 1
        if (idx + 1) % 250 == 0:
            cocotb.log.info("xval: %d/%d processed, %d failures",
                            idx + 1, len(SUBSET), len(failures))

    cocotb.log.info("xval shard %d/%d: PASS %d/%d",
                    SHARD, SHARDS, passed, len(SUBSET))
    if failures:
        for f in failures[:20]:
            cocotb.log.error("  %s", f)
    assert not failures, f"{len(failures)} CTU vectors failed (first: {failures[0]})"
