# CTU Full Cross-Validation

**Matched (ACK-only diff): 430**
**Mismatched: 63**
**Deferred (FD BRS=1, needs two-phase timing): 255**

## Per format

| Format | Verdict | Count |
|---|---|---|
| classic_base | ACK_ONLY_DIFF | 112 |
| classic_base | prefix_mismatch | 21 |
| classic_ext | ACK_ONLY_DIFF | 100 |
| classic_ext | prefix_mismatch | 16 |
| fd_base | ACK_ONLY_DIFF | 129 |
| fd_base | deferred_brs1 | 127 |
| fd_base | prefix_mismatch | 14 |
| fd_ext | ACK_ONLY_DIFF | 89 |
| fd_ext | deferred_brs1 | 128 |
| fd_ext | prefix_mismatch | 12 |

## Model-level format coverage (from CTU corpus)

| Format | Frames |
|---|---|
| classic_base | 112 |
| classic_ext | 100 |
| fd_base | 129 |
| fd_ext | 89 |

| CRC width | Frames |
|---|---|
| crc15 | 212 |
| crc17 | 218 |

| Format x CRC | Frames |
|---|---|
| classic_base x crc15 | 112 |
| classic_ext x crc15 | 100 |
| fd_base x crc17 | 129 |
| fd_ext x crc17 | 89 |

## Deferred (FD BRS=1) breakdown

| CRC width | Deferred frames |
|---|---|
| crc17 | 186 |
| crc21 | 69 |

| DLC | Deferred frames |
|---|---|
| dlc0 | 19 |
| dlc1 | 15 |
| dlc2 | 18 |
| dlc3 | 14 |
| dlc4 | 22 |
| dlc5 | 14 |
| dlc6 | 16 |
| dlc7 | 14 |
| dlc8 | 23 |
| dlc9 | 17 |
| dlc10 | 14 |
| dlc11 | 10 |
| dlc12 | 21 |
| dlc13 | 14 |
| dlc14 | 10 |
| dlc15 | 14 |

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
