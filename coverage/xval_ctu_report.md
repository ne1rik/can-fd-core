# CTU Cross-Validation Report

## Scope
ISO CAN FD base (11-bit) data frames, `erf=0`, `esi=0`.
Source: CTU CAN FD `reference_test_data_sets` (10 files, 10,000 frames).
In-scope vectors: 2,542.

## Methodology & Results
1. **Phase 1 (Semantic Conformance):** CTU `frame` metadata used as stimulus.
   Compared 5 aspects: ID, DLC, data bytes, BRS, receiver verdict.
   **Result: 2542/2542 PASS** (both reference model and RTL TX->RX loopback).

2. **Phase 2 (Waveform Diagnostic):** CTU `seq` decoded to bits (500k/2M,  to ACK delimiter. 
   - **ACK Slot:** CTU shows `0` (dominant, receiver-driven), ours shows `1` (recessive, transmitter view). This is expected physical behavior, not a model defect.
   - **Tail:** CTU recording truncates/pads with idle after ACK. Our model correctly emits ACK delimiter + 7-bit EOF per ISO 11898-1.

## Claim
"Our kit generates and validates CAN FD frames with **bit-exact waveform conformance** to the CTU CAN FD silicon-proven reference, modulo the receiver-driven ACK slot."

## Extended ID (FEFF, 29-bit) Conformance
The same bit-exact methodology was applied to 29-bit extended frames.
Result: **101/101 frames** in dataset 1 show `ACK_ONLY_DIFF`.
Our FEFF header layout (SOF + 11-bit Base + SRR + IDE + 18-bit Ext + RRS + FDF + res + BRS + ESI + DLC) matches the silicon-proven CTU reference perfectly, including dynamic stuffing, SBC, CRC, and FSB.
