# CAN FD bit timing — DUT #1 / bus model reference

Core clock: **80 MHz** (mtq = 12.5 ns). All values below are checked for
legality: `SJW <= TSEG2`, `TSEG2 >= 1`, exact target bit rate.

## Verified configuration

| Phase | Rate | BRP | tq | N (tq/bit) | SYNC | TSEG1 | TSEG2 | SJW | Sample point |
|---|---|---|---|---|---|---|---|---|---|
| Arbitration | 500 kbit/s | 2 | 25.0 ns | 80 | 1 | 63 | 16 | 4 | 80.00 % |
| Data (target) | 2 Mbit/s | 1 | 12.5 ns | 40 | 1 | 31 | 8 | 4 | 80.00 % |
| Data (max) | 5 Mbit/s | 1 | 12.5 ns | 16 | 1 | 12 | 3 | 3 | 81.25 % |

`N = 1 + TSEG1 + TSEG2`, `tq = BRP / f_core`, `sample_point = (1 + TSEG1) / N`.

Rate check: `80e6 / (2 * 80) = 500e3`, `80e6 / (1 * 40) = 2e6`, `80e6 / (1 * 16) = 5e6`.

## Legality rules enforced by the bus model

1. `SJW <= TSEG2` (the previous revision violated this at 5 Mbit/s: SJW=4, TSEG2=3).
2. `TSEG1 >= 1`, `TSEG2 >= 1`, SYNC is always 1 tq.
3. `N * tq` must equal the target bit time exactly (no rounding drift).
4. Register field widths are DUT-specific and must be checked by the adapter,
   not assumed by the bus model.

## Transmitter delay compensation (TDC / SSP)

The secondary sample point is measured **from the start of the transmitted bit**:

```
SSP = TDCV + TDCO
```

* `TDCV` — measured loop delay (transceiver + bus), in mtq. In simulation the
  default is `TDCV = 0` (no transceiver model); it is a per-node knob.
* `TDCO` — configured offset, in mtq. Recommended starting value equals the
  data-phase sample-point position:
  * 2 Mbit/s: `(1 + 31) = 32 tq = 32 mtq`
  * 5 Mbit/s: `(1 + 12) = 13 tq = 13 mtq`

The earlier revision of this file used `SSP = Prop_Seg + Phase_Seg1 + TDC_Offset`,
which is **not** the ISO definition and has been removed.

> Open item: the exact TDCV/TDCO quantisation and enable threshold must be
> cross-checked against CTU CAN FD documentation before the kit claims
> conformance. Tracked in the M1 report.
