# CTU Full Cross-Validation

**Matched (ACK-only diff): 493**
**Mismatched: 0**
**Deferred (FD BRS=1, needs two-phase timing): 255**

## Per format

| Format | Verdict | Count |
|---|---|---|
| classic_base | ACK_ONLY_DIFF | 133 |
| classic_ext | ACK_ONLY_DIFF | 116 |
| fd_base | ACK_ONLY_DIFF | 143 |
| fd_base | deferred_brs1 | 127 |
| fd_ext | ACK_ONLY_DIFF | 101 |
| fd_ext | deferred_brs1 | 128 |

## Model-level format coverage (from CTU corpus)

| Format | Frames |
|---|---|
| classic_base | 133 |
| classic_ext | 116 |
| fd_base | 143 |
| fd_ext | 101 |

| CRC width | Frames |
|---|---|
| crc15 | 249 |
| crc17 | 244 |

| Format x CRC | Frames |
|---|---|
| classic_base x crc15 | 133 |
| classic_ext x crc15 | 116 |
| fd_base x crc17 | 143 |
| fd_ext x crc17 | 101 |

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

