# Vector provenance and licence register

Every vector or reference used by the kit must have an entry here. 
No third-party RTL or testbench code is included in this repository.

## CTU CAN FD Licence Status (Critical)

The canonical repository (`github.com/Logic-Design-Services/CTU-CAN-FD`) uses a **dual-license model**:
- **2015–2020:** MIT License.
- **2021–Present:** Free for **non-commercial** use only. Commercial use is forbidden without a prior agreement with Logic Design Services Ltd.
- **Silicon Warning:** The license explicitly states: *"Anybody who wants to implement this IP core on silicon has to obtain a CAN protocol license from Bosch."*

**Consequences for this kit:**
1. We **DO NOT** bundle, copy, or redistribute any CTU RTL or VHDL testbench code.
2. CTU is used strictly as a "bring-your-own-clone" reference for local cross-validation.
3. Public CI **DOES NOT** run CTU tests to avoid license contamination.
4. Our kit is fully self-sufficient with its own Python/cocotb models and vectors.

## Register of Test Vectors

| ID | Description | Origin | Licence | Status |
|---|---|---|---|---|
| V-001 | FBFF, ID=0x5AA, DLC=8, data=8x0xFF, BRS=1 → CRC-17 = `0x006BD` | StackOverflow q/76852533 (Elmue C# `CanCrc` with MSB init, dw_infineon C demo). Matches public CANalyzer output. | Forum snippets (fair use for interoperability analysis) | `third-party-reported` |
| V-002 | CRC-17/CAN-FD catalogue check over `"123456789"` = `0x04F03` | CRC Catalogue (reveng), poly `0x1685B`, init 0, no reflection, xorout 0 | Public domain / CC0 | `primary-confirmed` |
| V-003 | CRC-21/CAN-FD catalogue check over `"123456789"` = `0x0ED841` | CRC Catalogue (reveng), poly `0x102899`, init 0 | Public domain / CC0 | `primary-confirmed` |
| V-004 | Bit-stuffing rule: 5 identical bits → 1 inverted bit, which starts the next run | ISO 11898-1:2015 §10.4.2.5 | ISO Standard (referenced) | `primary-confirmed` |

## Open Items
- Cross-check frame-level CRC convention (init=MSB, padding, stuffed+SC input) against CTU's actual testbench behavior to promote V-001 to `primary-confirmed`. (Task 1.5)
