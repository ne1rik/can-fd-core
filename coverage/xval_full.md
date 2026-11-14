# CTU Full Cross-Validation

**Matched (ACK-only diff): 4999**
**Mismatched: 0**
**Deferred (FD BRS=1, needs two-phase timing): 2539**

## Per format

| Format | Verdict | Count |
|---|---|---|
| classic_base | ACK_ONLY_DIFF | 1238 |
| classic_ext | ACK_ONLY_DIFF | 1246 |
| fd_base | ACK_ONLY_DIFF | 1281 |
| fd_base | deferred_brs1 | 1261 |
| fd_ext | ACK_ONLY_DIFF | 1234 |
| fd_ext | deferred_brs1 | 1278 |

## Model-level format coverage (from CTU corpus)

| Format | Frames |
|---|---|
| classic_base | 1238 |
| classic_ext | 1246 |
| fd_base | 1281 |
| fd_ext | 1234 |

| CRC width | Frames |
|---|---|
| crc15 | 2484 |
| crc17 | 2515 |

| Format x CRC | Frames |
|---|---|
| classic_base x crc15 | 1238 |
| classic_ext x crc15 | 1246 |
| fd_base x crc17 | 1281 |
| fd_ext x crc17 | 1234 |

NOTE: RTL coverage remains FBFF-scoped until RTL supports all formats.

