# CAN FD Functional Coverage

**Overall: 56.5%** (points 89.7%, crosses 48.4%)

## CoverPoints

| Group | Covered | Total | % |
|---|---|---|---|
| dlc | 16 | 16 | 100.0% |
| brs | 2 | 2 | 100.0% |
| crc_width | 2 | 2 | 100.0% |
| data_pattern | 5 | 5 | 100.0% |
| id_range | 5 | 5 | 100.0% |
| stuff_density | 4 | 4 | 100.0% |
| error_type | 1 | 5 | 20.0% |

## CoverCrosses

| Cross | Covered | Legal | % |
|---|---|---|---|
| dlc_x_brs | 32 | 32 | 100.0% |
| id_x_pattern | 25 | 25 | 100.0% |
| error_x_dlc | 16 | 79 | 20.3% |
| fault_x_pattern | 5 | 25 | 20.0% |

## Uncovered

- **error_type**: payload_flip, crc_flip, stuff_flip, sc_flip
- **error_x_dlc**: payload_flip x 1, payload_flip x 2, payload_flip x 3, payload_flip x 4, payload_flip x 5, payload_flip x 6, payload_flip x 7, payload_flip x 8, payload_flip x 9, payload_flip x 10, payload_flip x 11, payload_flip x 12, ... +51 more
- **fault_x_pattern**: payload_flip x zeros, payload_flip x ones, payload_flip x alternating, payload_flip x ramp, payload_flip x random, crc_flip x zeros, crc_flip x ones, crc_flip x alternating, crc_flip x ramp, crc_flip x random, stuff_flip x zeros, stuff_flip x ones, ... +8 more
