# CTU Full Cross-Validation

**Matched (ACK-only diff): 249**
**Mismatched: 244**
**Deferred (FD BRS=1, needs two-phase timing): 255**

## Per format

| Format | Verdict | Count |
|---|---|---|
| classic_base | ACK_ONLY_DIFF | 133 |
| classic_ext | ACK_ONLY_DIFF | 116 |
| fd_base | deferred_brs1 | 127 |
| fd_base | prefix_mismatch | 143 |
| fd_ext | deferred_brs1 | 128 |
| fd_ext | prefix_mismatch | 101 |

## Model-level format coverage (from CTU corpus)

| Format | Frames |
|---|---|
| classic_base | 133 |
| classic_ext | 116 |

| CRC width | Frames |
|---|---|
| crc15 | 249 |

| Format x CRC | Frames |
|---|---|
| classic_base x crc15 | 133 |
| classic_ext x crc15 | 116 |

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

CRC widths with ZERO independent waveform confirmation: **crc17, crc21**

These widths appear only in the deferred BRS=1 subset. Two-phase bit
timing (sample point + SSP) is required to close this gap.

NOTE: RTL coverage remains FBFF-scoped until RTL supports all formats.

## Failures (first 20)

- ds1 fd_ext id=0x1127cf88 dlc=10 prefix_mismatch @ 182
- ds1 fd_base id=0x749 dlc=3 prefix_mismatch @ 53
- ds1 fd_base id=0x62d dlc=10 prefix_mismatch @ 159
- ds1 fd_ext id=0x1a458f15 dlc=1 prefix_mismatch @ 58
- ds1 fd_base id=0x501 dlc=5 prefix_mismatch @ 76
- ds1 fd_base id=0xf9 dlc=9 prefix_mismatch @ 128
- ds1 fd_base id=0x7cc dlc=5 prefix_mismatch @ 71
- ds1 fd_base id=0x204 dlc=6 prefix_mismatch @ 81
- ds1 fd_ext id=0x1578caa4 dlc=7 prefix_mismatch @ 109
- ds1 fd_ext id=0x191429ab dlc=1 prefix_mismatch @ 57
- ds1 fd_base id=0x159 dlc=3 prefix_mismatch @ 58
- ds1 fd_base id=0x54c dlc=9 prefix_mismatch @ 129
- ds1 fd_base id=0x743 dlc=3 prefix_mismatch @ 54
- ds1 fd_ext id=0x1fddb240 dlc=7 prefix_mismatch @ 108
- ds1 fd_base id=0xd4 dlc=4 prefix_mismatch @ 63
- ds1 fd_ext id=0x771d2ec dlc=1 prefix_mismatch @ 56
- ds1 fd_base id=0x4b6 dlc=4 prefix_mismatch @ 62
- ds1 fd_ext id=0xd9ea9b3 dlc=2 prefix_mismatch @ 65
- ds1 fd_base id=0x689 dlc=5 prefix_mismatch @ 70
- ds1 fd_ext id=0x1a5b650 dlc=4 prefix_mismatch @ 87
