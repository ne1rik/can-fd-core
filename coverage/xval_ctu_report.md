# CTU Cross-Validation Report

## Scope
Data frames (`rtr=0`), no injected error (`erf=0`), `esi=0`.
Source: CTU CAN FD `reference_test_data_sets` (10 files, 10,000 frames).

## Methodology & Results
1. **Model-level conformance:** CTU `frame` metadata used as stimulus.
   Compared 5 aspects: ID, DLC, data bytes, BRS, receiver verdict.
   **Result: 4999/4999 MATCHED** (bit-exact modulo receiver-driven ACK).
   **Mismatched: 0**
   **Deferred: 2539** (FD BRS=1, requires two-phase timing simulation).

2. **RTL-level conformance:** 
   - **FBFF (CAN FD Base):** Proven. 100% coverage, 9/9 RTL mutations killed, all loopback/inject tests pass.
   - **Classic / FEFF:** **UNPROVEN.** RTL code exists but currently fails vector tests (0 vectors executed due to extractor/filter mismatch, and DUT not parameterized in default builds). Suspected bugs in DLC mapping and in-place stuffing logic.

## Validation Gap
CRC widths with ZERO independent waveform confirmation: **crc21**.
These widths appear only in the deferred BRS=1 subset. Two-phase bit timing (sample point + SSP) is required to close this gap.

## Next Steps
1. Fix Classic/FEFF RTL bugs (DLC indexing, stuffing buffer overlap).
2. Parameterize DUT builds (done) and run vector tests with `EXTENDED`/`CLASSIC` flags.
3. Decouple tests from DUT internals (VIP Agent architecture) to enable true multi-DUT validation.
