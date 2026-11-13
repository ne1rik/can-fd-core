# CAN FD verification kit (work in progress) + CAN FD TX core

An open, simulation-only CAN FD verification infrastructure built on
**Verilator + cocotb**, with no commercial EDA licences required.
The repository also contains a CAN FD transmitter core used as **DUT #1**.

**This is not an industrial IP block and no conformance certificate is claimed.**
Protocol target: **ISO 11898-1:2015 only** (the free Bosch CAN FD 1.0 spec from
2012 is *non-ISO* and is deliberately not used).

## Status (real runs only)

| Component | State | Evidence |
|---|---|---|
| `rtl/can_fd_tx.sv` (DUT #1, TX) | working | `make` → 6/6 PASS |
| `rtl/bit_stuffer.sv` | working, standalone | 2/2 PASS |
| `rtl/crc17_canfd.sv` | working, standalone | 3/3 PASS |
| `rtl/crc_canfd.sv` (17/21) | working, standalone | 1/1 PASS |
| `rtl/can_fd_ctrl.sv` (APB3 stub) | placeholder | `make -f Makefile.aux` → 3/3 PASS |
| Reference model (Python) | ISO framing | anchor CRC-17 `0x006BD` matches a third-party CANalyzer vector (StackOverflow q/76852533); pending CTU cross-check |
| `canfd_kit/` (bus, injector, checker, coverage, vectors) | **not started** | — |
| RX path, 29-bit ID, CRC-15, error frames, TEC/REC, bus-off | **not implemented** | — |
| GitHub Actions | **not yet confirmed green** | — |

## Quickstart

```bash
make                 # TX regression, expect TESTS=6 PASS=6
make -f Makefile.aux # APB3 stub + reference-model anchors + CTRL polarity lock
bash scripts/smoke.sh  # dependency smoke report -> docs/smoke_report.md
python3 scripts/frame_decomp.py  # field-by-field frame decomposition
```

## Two CRC conventions — do not mix them up

| Scope | Init | Where | Reference check |
|---|---|---|---|
| Pure catalogue algorithm | `0` | `rtl/crc17_canfd.sv`, `rtl/crc_canfd.sv`, `calculate_crc()` | CRC-17 `0x04F03`, CRC-21 `0x0ED841` over `"123456789"` |
| ISO **frame-level** CRC | MSB set (`0x10000` / `0x100000`) | `rtl/can_fd_tx.sv`, `generate_can_fd_frame()` | ID=0x5AA, 8x0xFF → CRC-17 `0x006BD` (third-party-reported, see `docs/vectors_provenance.md`) |

Frame-level CRC is computed over the **dynamically stuffed** bit stream **plus
the 4-bit stuff count** (Gray-coded + even parity). Fixed stuff bits in the CRC
field are **not** part of the CRC calculation.

## Known limitations

* TX only. No receiver, no error signalling, no fault confinement state machine.
* 11-bit identifiers only (FBFF). FEFF / SRR / IDE arbitration not implemented.
* No CRC-15 (classical CAN frames) yet.
* TDC/SSP is modelled with `TDCV = 0` by default; quantisation and enable
  threshold still to be cross-checked against CTU CAN FD.
* Functional coverage (`cocotb-coverage`) is not wired in yet.

## Reference behaviour and licence caution

Behavioural reference: **CTU CAN FD**
(`github.com/Logic-Design-Services/CTU-CAN-FD`).

**Licence caution.** An earlier revision of this README described their RTL as
MIT. That claim was taken from a project brief and was **not verified**; it is
withdrawn. Reports indicate the canonical repository licenses commercial use of
both RTL and testbench under a paid licence (contact: Ondrej Ille), with the
Linux driver under GPLv2. Earlier MIT references appear to describe old mirrors.
The actual LICENSE file must be read and recorded before any reuse.

Consequences for this kit:
* the kit is **self-sufficient**: our own vectors, our own provenance records;
* CTU appears in `examples/` only as *bring-your-own-clone* plus an adapter;
* **no CTU artefacts** are redistributed in this MIT-licensed repository;
* **CTU is not run in public CI**;
* their RTL is never copied into our code.

Vector provenance and licence status are recorded in `docs/vectors_provenance.md`.

## Licence

MIT — see `LICENSE`.
