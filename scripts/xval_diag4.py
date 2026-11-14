#!/usr/bin/env python3
"""Clean comparison: strip both idle ends, then diff."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "tb"))

from can_fd_reference import generate_can_fd_frame, _raw_of, stuff_bits, dlc_len
from scripts.xval_ctu_parser import parse_vhdl_reference_data, filter_can_fd_base_frames


def expand_ctu(seq, bit_ns=2000, idle_thresh=50000):
    """Expand RLE to bits, removing leading and trailing idle entries."""
    # strip leading long-idle entries
    s = 0
    while s < len(seq) and seq[s][0] == 1 and seq[s][1] > idle_thresh:
        s += 1
    # strip trailing long-idle entries
    e = len(seq)
    while e > s and seq[e-1][0] == 1 and seq[e-1][1] > idle_thresh:
        e -= 1
    
    bits = []
    for lvl, dur in seq[s:e]:
        n = round(dur / bit_ns)
        bits.extend([lvl] * n)
    return bits


def fmt(bits, start, end):
    return ''.join(str(b) for b in bits[max(0,start):end])


def main():
    path = sys.argv[1]
    frames = filter_can_fd_base_frames(parse_vhdl_reference_data(path))
    print(f"{len(frames)} CAN FD base frames\n")

    for i, f in enumerate(frames[:3]):
        fr = f['frame']
        n = dlc_len(fr['dlc'])
        data = fr['data'][:n]
        ours = generate_can_fd_frame(fr['identifier'], fr['dlc'], data, fr['brs'] == 1)

        ctu = expand_ctu(f['seq'])
        
        print(f"=== Frame {i}: ID={fr['identifier']:#05x} DLC={fr['dlc']} BRS={fr['brs']} ===")
        print(f"  ours={len(ours)}, CTU={len(ctu)}")
        
        if len(ours) != len(ctu):
            print(f"  LENGTH DIFF: {len(ctu) - len(ours)}")
        
        # bit-by-bit diff
        ml = max(len(ours), len(ctu))
        diffs = [j for j in range(ml) if j >= len(ours) or j >= len(ctu) or ours[j] != ctu[j]]
        if not diffs:
            print("  PERFECT MATCH")
        else:
            print(f"  {len(diffs)} bit diffs at positions: {diffs[:20]}{'...' if len(diffs)>20 else ''}")
            # show context around first 3 diffs
            for d in diffs[:3]:
                lo = max(0, d-8)
                hi = d + 12
                print(f"  --- diff at {d} ---")
                print(f"    ours[{lo}:{hi}] = {fmt(ours, lo, hi)}")
                print(f"    CTU [{lo}:{hi}] = {fmt(ctu, lo, hi)}")
                print(f"    {''.join('^' if j==d else ' ' for j in range(lo,hi))}")
        print()


if __name__ == "__main__":
    main()
