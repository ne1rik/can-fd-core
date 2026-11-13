# CTU Cross-Validation Report

## Scope
ISO CAN FD base (11-bit) data frames, `erf=0`, `esi=0`.
Source: CTU CAN FD `reference_test_data_sets` (10 files, 10,000 frames).
In-scope vectors: 2,542.

## Methodology
1. **Phase 1 (Semantic Conformance):** CTU `frame` metadata used as stimulus.
   Compared 5 aspects: ID, DLC, data bytes, BRS, receiver verdict.
   Result: **2542/2542 PASS** (both reference model and RTL TX->RX loopback).

2. **Phase 2 (Waveform Diagnostic):** CTU `seq` decoded to bits (500k/2M, 80% sample).
   Finding: Perfect match in header, arbitration, and data fields.
   **Documented Gap:** CTU `seq` recording truncates immediately after the
   dominant ACK slot, followed by long idle. Our ISO-compliant model emits
   the full tail: CRC delimiter + ACK + ACK delimiter + EOF (7 bits).
   This is an abstraction difference, not a model defect. We deliberately
   do not truncate our model to match CTU's recording window, as that would
   violate ISO 11898-1 and break all other verification tests.

## Claim
"Our kit decodes and validates the same CTU reference frames at the field
and verdict level with 100% conformance."
