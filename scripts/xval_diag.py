#!/usr/bin/env python3
"""Diagnose CTU seq encoding: find the bit-time and expansion that matches."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "tb"))

from can_fd_reference import generate_can_fd_frame, dlc_len
from scripts.xval_ctu_parser import parse_vhdl_reference_data, filter_can_fd_base_frames


def expand(seq, bit_ns, idle_thresh=20000):
    # drop leading/trailing LONG idle (inter-frame space), keep EOF
    s = 0
    while s < len(seq) and seq[s][1] > idle_thresh:
        s += 1
    e = len(seq)
    while e > s and seq[e-1][1] > idle_thresh:
        e -= 1
    bits = []
    for lvl, dur in seq[s:e]:
        n = round(dur / bit_ns)
        bits.extend([lvl] * n)
    return bits


def main():
    path = sys.argv[1]
    frames = filter_can_fd_base_frames(parse_vhdl_reference_data(path))
    print(f"{len(frames)} CAN FD base frames\n")

    # look at first 6 frames, try several bit-times
    for i, f in enumerate(frames[:6]):
        fr = f['frame']
        n = dlc_len(fr['dlc'])
        ours = generate_can_fd_frame(fr['identifier'], fr['dlc'], fr['data'][:n], fr['brs'] == 1)
        durs = [d for _, d in f['seq']]
        print(f"Frame {i}: ID={fr['identifier']:#05x} DLC={fr['dlc']} BRS={fr['brs']} "
              f"seq_entries={len(f['seq'])} seq_len={f['seq_len']} ours={len(ours)}")
        print(f"  durations sample: {durs[:12]}")
        for bit_ns in (2000, 1000, 500, 250):
            b = expand(f['seq'], bit_ns)
            mark = "  <== MATCH" if len(b) == len(ours) else ""
            print(f"  bit_ns={bit_ns:5d} -> {len(b):4d} bits{mark}")
        print()


if __name__ == "__main__":
    main()
