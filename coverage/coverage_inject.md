# CAN FD Functional Coverage

**Overall: 81.1%** (points 76.9%, crosses 82.4%)

## CoverPoints

| Group | Covered | Total | % |
|---|---|---|---|
| dlc | 16 | 16 | 100.0% |
| brs | 2 | 2 | 100.0% |
| crc_width | 2 | 2 | 100.0% |
| data_pattern | 1 | 5 | 20.0% |
| id_range | 1 | 5 | 20.0% |
| stuff_density | 3 | 4 | 75.0% |
| error_type | 5 | 5 | 100.0% |

## CoverCrosses

| Cross | Covered | Legal | % |
|---|---|---|---|
| dlc_x_brs | 32 | 32 | 100.0% |
| id_x_pattern | 1 | 25 | 4.0% |
| error_x_dlc | 79 | 79 | 100.0% |

## Uncovered

- **data_pattern**: ones, alternating, ramp, random
- **id_range**: 0x001-0x1FF, 0x200-0x3FF, 0x400-0x5FF, 0x600-0x7FF
- **stuff_density**: none
- **id_x_pattern**: 0x000 x ones, 0x000 x alternating, 0x000 x ramp, 0x000 x random, 0x001-0x1FF x zeros, 0x001-0x1FF x ones, 0x001-0x1FF x alternating, 0x001-0x1FF x ramp, 0x001-0x1FF x random, 0x200-0x3FF x zeros, 0x200-0x3FF x ones, 0x200-0x3FF x alternating, ... +12 more
