# CTU Cross-Validation — Phase 1 (semantic conformance)

Scope: ISO CAN FD base (11-bit) data frames, erf=0, esi=0.
Source: CTU CAN FD reference_test_data_sets (10 files, 10000 frames).
In-scope vectors: 2542.

## Method
CTU `frame` metadata used as stimulus. CTU `seq` waveform deliberately NOT
compared: it is a timed bus trace (500k/2M, 80% sample point, idle/ACK/EOF
window), a different abstraction level.

Five aspects compared per vector: ID, DLC, data bytes, BRS, receiver verdict.

## Results
- Reference model: 2542/2542 PASS
- RTL TX->RX loopback (4 shards): 636+636+635+635 = 2542/2542 PASS

## Claim
"Our kit decodes and validates the same CTU reference frames at field/verdict
level." NOT a bit-accurate waveform match against CTU.
