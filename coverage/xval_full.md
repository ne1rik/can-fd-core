# CTU Full Cross-Validation

**Matched (ACK-only diff): 4332**
**Mismatched: 667**
**Deferred (FD BRS=1, needs two-phase timing): 2539**

## Per format

| Format | Verdict | Count |
|---|---|---|
| classic_base | ACK_ONLY_DIFF | 1071 |
| classic_base | ack_unexpected | 3 |
| classic_base | prefix_mismatch | 164 |
| classic_ext | ACK_ONLY_DIFF | 1036 |
| classic_ext | prefix_mismatch | 210 |
| fd_base | ACK_ONLY_DIFF | 1162 |
| fd_base | deferred_brs1 | 1261 |
| fd_base | prefix_mismatch | 119 |
| fd_ext | ACK_ONLY_DIFF | 1063 |
| fd_ext | deferred_brs1 | 1278 |
| fd_ext | prefix_mismatch | 171 |

## Model-level format coverage (from CTU corpus)

| Format | Frames |
|---|---|
| classic_base | 1071 |
| classic_ext | 1036 |
| fd_base | 1162 |
| fd_ext | 1063 |

| CRC width | Frames |
|---|---|
| crc15 | 2107 |
| crc17 | 2225 |

| Format x CRC | Frames |
|---|---|
| classic_base x crc15 | 1071 |
| classic_ext x crc15 | 1036 |
| fd_base x crc17 | 1162 |
| fd_ext x crc17 | 1063 |

## Deferred (FD BRS=1) breakdown

| CRC width | Deferred frames |
|---|---|
| crc17 | 1684 |
| crc21 | 855 |

| DLC | Deferred frames |
|---|---|
| dlc0 | 160 |
| dlc1 | 158 |
| dlc2 | 160 |
| dlc3 | 142 |
| dlc4 | 150 |
| dlc5 | 149 |
| dlc6 | 142 |
| dlc7 | 149 |
| dlc8 | 158 |
| dlc9 | 147 |
| dlc10 | 169 |
| dlc11 | 179 |
| dlc12 | 161 |
| dlc13 | 178 |
| dlc14 | 178 |
| dlc15 | 159 |

## VALIDATION GAP

CRC widths with ZERO independent waveform confirmation: **crc21**

These widths appear only in the deferred BRS=1 subset. Two-phase bit
timing (sample point + SSP) is required to close this gap.

NOTE: RTL coverage remains FBFF-scoped until RTL supports all formats.

## Failures (first 20)

- ds1 fd_base id=0x501 dlc=5 prefix_mismatch @ 53
- ds1 classic_base id=0x4f9 dlc=4 prefix_mismatch @ 50
- ds1 fd_ext id=0x1705df69 dlc=9 prefix_mismatch @ 52
- ds1 classic_ext id=0x612c960 dlc=3 prefix_mismatch @ 43
- ds1 fd_ext id=0x1f3247c1 dlc=6 prefix_mismatch @ 32
- ds1 classic_base id=0x676 dlc=3 prefix_mismatch @ 30
- ds1 classic_base id=0x117 dlc=6 prefix_mismatch @ 47
- ds1 classic_base id=0x135 dlc=7 prefix_mismatch @ 61
- ds1 fd_base id=0x280 dlc=3 prefix_mismatch @ 28
- ds1 fd_base id=0x3be dlc=3 prefix_mismatch @ 27
- ds1 fd_ext id=0x1f6ff0d6 dlc=3 prefix_mismatch @ 29
- ds1 classic_base id=0x7d dlc=2 prefix_mismatch @ 10
- ds1 classic_ext id=0x4643534 dlc=4 prefix_mismatch @ 55
- ds1 classic_base id=0x1ea dlc=6 prefix_mismatch @ 75
- ds1 fd_base id=0x59f dlc=6 prefix_mismatch @ 51
- ds1 classic_ext id=0xc6ff0b6 dlc=1 prefix_mismatch @ 27
- ds1 classic_base id=0x7f2 dlc=7 prefix_mismatch @ 22
- ds1 fd_base id=0x605 dlc=9 prefix_mismatch @ 71
- ds1 fd_ext id=0xa99029 dlc=9 prefix_mismatch @ 125
- ds1 classic_ext id=0x43cb4db dlc=4 prefix_mismatch @ 64
