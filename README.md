# CAN FD Verification Kit + RTL Core

Simulation-only CAN FD verification infrastructure and an RTL core built on **Verilator + cocotb**. No commercial EDA licences are required.

**Protocol target:** ISO 11898-1:2015. The free Bosch CAN FD 1.0 (2012) document is *non-ISO* and is deliberately not used as a reference.

**Not an industrial IP block. No conformance certificate is claimed.**

[Русская версия](README.ru.md)

---

## What this is

Two components that verify each other:
1. **A bit-exact Python reference model** (`tb/can_fd_reference.py`) that builds CAN and CAN FD frames: dynamic bit stuffing, stuff-count field, CRC-15/17/21.
2. **An RTL core** (`rtl/`) — transmitter, receiver, two-phase bit timing — plus a loopback wrapper used as DUT #1.

Every claim in this repository is backed by a run whose log is kept in `logs/`.

## Verified results

| Gate | Result | Source |
|---|---|---|
| CTU vectors through RTL | 7538 / 7538, 0 failures | `logs/ctu_*.log` |
| Model-vs-RTL sweep | 5216 cases, 0 failures | `logs/big_*.log` |
| CRC-boundary stuffing | 80 cases, 0 failures | `logs/bnd_*.log` |
| Model unit tests (pytest) | 248 passed | `logs/regress.log` |
| Model vs CTU waveforms | 4999 matched, 0 mismatch, 2539 deferred | `logs/xval_model.log` |
| Mutation testing | 12 / 12 killed, 0 gaps, 0 problems | `logs/mutation_model.log` |

**Corpus:** 7553 vectors — 1238 Classic Base, 1246 Classic Extended, 2557 FD Base, 2512 FD Extended. Extracted from the open CTU CAN FD reference dataset. 15 synthetic FD frames (DLC 11–15, BRS=0) were added to close a CRC-21 mutation gap.

**Deferred:** 2539 FD BRS=1 vectors are excluded from the fixed-rate waveform cross-check because it cannot follow a mid-frame bit-rate switch. Those frames are covered instead by the real-timing matrix.

## Architecture

| Path | Role |
|---|---|
| `rtl/can_fd_tx.sv` | Transmitter: framing, dynamic stuffing, stuff count, CRC-15/17/21 |
| `rtl/can_fd_rx.sv` | Receiver: de-stuffing, CRC check, form checks, ACK drive |
| `rtl/can_bit_timing.sv` | NBT/DBT bit timing, sample point, SSP offset, phase realignment |
| `rtl/can_fd_loopback.sv` | TX + RX wired through a dominant-AND bus |
| `tb/can_fd_reference.py` | Bit-exact Python oracle |
| `scripts/mutation_model.py` | Mutation harness over the reference model |
| `scripts/verify_all.sh` | Full gate runner, writes `logs/` |

Formats supported: Classic CAN base/extended (CRC-15) and CAN FD base/extended (CRC-17 for DLC ≤ 8, CRC-21 for DLC ≥ 9), DLC 0–15, BRS on/off.

## Quickstart

Requirements: Verilator ≥ 5.0, cocotb ≥ 2.0, Python ≥ 3.10.

```bash
# Full gate run. Writes logs/ and prints a summary.
bash scripts/verify_all.sh

# Model mutation testing (12 mutants).
python3 scripts/mutation_model.py

# Bit-timing units.
make -f Makefile.bittiming TEST_MODULES=tests.test_bit_timing

# Real two-phase timing matrix. Use a dedicated SIM_BUILD to avoid stale binaries.
make -f Makefile.loopback \
    SIM_BUILD=$PWD/sim_build_rt \
    EXTENDED=0 CLASSIC=0 \
    NBT_PRESCALER=1 NBT_TSEG1=12 NBT_TSEG2=4 \
    DBT_PRESCALER=1 DBT_TSEG1=3 DBT_TSEG2=1 \
    TEST_MODULES=tests.test_timing_matrix
```

## Known limitations

* **Fault confinement is not implemented.** TEC/REC counters, error frames and bus-off are out of scope of the current core.
* **Prescaler > 1 with a very short data phase.** With `NBT_PRESCALER=2` and `DBT=3` clocks the SOF hard-sync can slip by 1–2 clocks. This is a pre-existing resynchronisation limitation, not a regression.
* **Simulation only.** No FPGA build, no silicon, no ISO 26262 qualification.
* **2539 BRS=1 vectors deferred** in the waveform cross-check, as described above.

## Licence and contact

Provided for research and evaluation. Contact details are supplied to the report generator via `--author/--email/--repo` and are not stored in this file.
