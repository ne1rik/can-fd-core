# Vector provenance and licence register

Every vector used by the kit must have an entry here: origin, licence status,
and verification status. No vector enters the regression suite without one.

## Status vocabulary

* `primary-confirmed` — checked against the standard text or a silicon-proven
  reference implementation run by us.
* `third-party-reported` — value published by a named third party and
  reproduced by our model; **not** primary-confirmed.
* `unverified` — no reproducible origin. Must not be used as a regression anchor.

## Register

| ID | Description | Origin | Licence | Status |
|---|---|---|---|---|
| V-001 | FBFF, ID=0x5AA, DLC=8, data=8x0xFF, BRS=1, ESI=0 → CRC-17 = `0x006BD` | StackOverflow q/76852533 "How to calculate CRC for ISO CAN-FD frames": answer by Elmue (C# `CanCrc`, init = MSB) and answer by dw_infineon (C demo printing `Expected (CANalyzer) = 0x006BD`); Mark Adler's answer states the 17 zero bits must NOT be appended | forum code snippets, quoted for interoperability analysis; no CTU artefact involved | `third-party-reported` |
| V-002 | CRC-17/CAN-FD catalogue check over `"123456789"` = `0x04F03` | CRC catalogue (reveng), poly `0x1685B`, init 0, no reflection, xorout 0 | public catalogue | `primary-confirmed` (algorithm level) |
| V-003 | CRC-21/CAN-FD catalogue check over `"123456789"` = `0x0ED841` | CRC catalogue (reveng), poly `0x102899`, init 0 | public catalogue | `primary-confirmed` (algorithm level) |

## Open items blocking anchor promotion

1. **V-001 must not become a kit regression anchor** until the frame-level CRC
   convention (init, padding, CRC input composition) is cross-checked against
   CTU CAN FD reference tests. Gate item in task 1.5.
2. **Frame-length semantics.** ISO frame boundary = end of EOF. IFS (3 bits) is
   NOT part of the frame. Our model emits a 10-bit tail
   (CRC delimiter + ACK slot + ACK delimiter + EOF x 7) and no IFS; verified by
   `scripts/frame_decomp.py`. Any external reference implementation must print
   the same field decomposition before lengths are compared.
3. **CTU licence.** Read the actual LICENSE file in the canonical repository and
   record the exact terms here before deriving anything from their testbench.
   Until then: no CTU artefacts in this repository, no CTU in public CI.
