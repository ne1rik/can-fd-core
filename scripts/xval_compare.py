#!/usr/bin/env python3
"""Cross-validation: compare CTU reference vs our model."""

import sys
from pathlib import Path

script_dir = Path(__file__).parent
root_dir   = script_dir.parent
tb_dir     = root_dir / "tb"
sys.path.insert(0, str(root_dir))
sys.path.insert(0, str(tb_dir))

from can_fd_reference import generate_can_fd_frame, dlc_to_bytes
from scripts.xval_ctu_parser import (
    parse_vhdl_reference_data, filter_can_fd_base_frames,
    seq_to_bitstream, strip_idle, _first_diff,
)


def main():
    if len(sys.argv) < 2:
        print("Usage: xval_compare.py <vhd> [debug]")
        sys.exit(1)

    vhd = sys.argv[1]
    debug = 'debug' in sys.argv

    frames = filter_can_fd_base_frames(parse_vhdl_reference_data(vhd))
    print(f"Validating {len(frames)} CAN FD base frames from {Path(vhd).name}\n")

    passed = failed = 0
    fail_examples = []

    for i, f in enumerate(frames):
        fr = f['frame']
        fid, dlc, brs = fr['identifier'], fr['dlc'], fr['brs'] == 1
        n = dlc_to_bytes(dlc)
        data = fr['data'][:n]

        ours = generate_can_fd_frame(fid, dlc, data, brs)
        ctu  = seq_to_bitstream(f['seq'], our_bits=ours, brs=brs,
                                debug=(debug and i < 3))

        ok = (ctu == ours)
        if ok:
            passed += 1
            print(f"Frame {i:3d}: ID={fid:#05x} DLC={dlc:2d} BRS={int(brs)} "
                  f"len={len(ctu):3d}  PASS")
        else:
            failed += 1
            fd = _first_diff(ctu, ours)
            print(f"Frame {i:3d}: ID={fid:#05x} DLC={dlc:2d} BRS={int(brs)} "
                  f"CTU={len(ctu):3d} ours={len(ours):3d}  FAIL "
                  f"(first diff={fd})")
            if len(fail_examples) < 3:
                fail_examples.append((i, fr, f['seq'], ctu, ours))
                print(f"    CTU[0:40]={''.join(map(str, ctu[:40]))}")
                print(f"    our[0:40]={''.join(map(str, ours[:40]))}")

    print(f"\nSummary: {passed} passed, {failed} failed out of {len(frames)}")

    if fail_examples and debug:
        print("\n" + "="*70)
        print("DEBUG: first failing frame details")
        print("="*70)
        idx, fr, seq, ctu, ours = fail_examples[0]
        real = strip_idle(seq)
        print(f"\nFrame {idx}: ID={fr['identifier']:#05x} DLC={fr['dlc']} "
              f"BRS={fr['brs']} data={[hex(b) for b in fr['data'][:8]]}")
        print(f"Raw seq: {len(seq)} entries, stripped: {len(real)} entries")
        print(f"CTU bits: {len(ctu)}, our bits: {len(ours)}")
        print(f"\nFirst 20 stripped entries (level, duration → slow bits / fast bits):")
        for k in range(min(20, len(real))):
            lvl, dur = real[k]
            sb = round(dur / 2000)
            fb = round(dur / 500)
            print(f"  [{k:2d}] ({lvl}, {dur:6d} ns) → {sb} slow / {fb} fast")
        print(f"\nCTU vs ours, first 60 bits:")
        print(f"  CTU: {''.join(map(str, ctu[:60]))}")
        print(f"  our: {''.join(map(str, ours[:60]))}")
        diffs = [k for k in range(min(len(ctu), len(ours))) if ctu[k] != ours[k]]
        print(f"  Diff positions (first 20): {diffs[:20]}")
        if diffs:
            d = diffs[0]
            lo, hi = max(0, d-5), d+15
            print(f"  Around bit {d}:")
            print(f"    CTU[{lo}:{hi}]: {''.join(map(str, ctu[lo:hi]))}")
            print(f"    our[{lo}:{hi}]: {''.join(map(str, ours[lo:hi]))}")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
