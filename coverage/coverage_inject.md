# CAN FD Functional Coverage

**Overall: 91.0%** (points 92.3%, crosses 90.7%)

## CoverPoints

| Group | Covered | Total | % |
|---|---|---|---|
| dlc | 16 | 16 | 100.0% |
| brs | 2 | 2 | 100.0% |
| crc_width | 2 | 2 | 100.0% |
| data_pattern | 5 | 5 | 100.0% |
| id_range | 2 | 5 | 40.0% |
| stuff_density | 4 | 4 | 100.0% |
| error_type | 5 | 5 | 100.0% |

## CoverCrosses

| Cross | Covered | Legal | % |
|---|---|---|---|
| dlc_x_brs | 32 | 32 | 100.0% |
| id_x_pattern | 10 | 25 | 40.0% |
| error_x_dlc | 79 | 79 | 100.0% |
| fault_x_pattern | 25 | 25 | 100.0% |

## Uncovered

- **id_range**: 0x200-0x3FF, 0x400-0x5FF, 0x600-0x7FF
- **id_x_pattern**: 0x200-0x3FF x zeros, 0x200-0x3FF x ones, 0x200-0x3FF x alternating, 0x200-0x3FF x ramp, 0x200-0x3FF x random, 0x400-0x5FF x zeros, 0x400-0x5FF x ones, 0x400-0x5FF x alternating, 0x400-0x5FF x ramp, 0x400-0x5FF x random, 0x600-0x7FF x zeros, 0x600-0x7FF x ones, ... +3 more
