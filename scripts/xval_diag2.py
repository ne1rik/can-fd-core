#!/usr/bin/env python3
"""Honest bit-by-bit comparison to see WHERE they diverge."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "tb"))

from can_fd_reference import generate_can_fd_frame, dlc_len
from scripts.xval_ctu_parser import parse_vhdl_reference_data, filter_can_fd_base_frames


def show(name, bits):
    s = "".join(str(b) for b in bits[:40])
    print(f"  {name} (len={len(bits):3d}): {s}{'...' if len(bits) > 40 else ''}")


def main():
    path = sys.argv[1]
    frames = filter_can_fd_base_frames(parse_vhdl_reference_data(path))
    print(f"{len(frames)} CAN FD base frames\n")

    for i, f in enumerate(frames[:3]):
        fr = f['frame']
        n = dlc_len(fr['dlc'])
        data = fr['data'][:n]
        ours = generate_can_fd_frame(fr['identifier'], fr['dlc'], data, fr['brs'] == 1)

        print(f"=== Frame {i}: ID={fr['identifier']:#05x} DLC={fr['dlc']} BRS={fr['brs']} ===")
        print(f"  Data: {[hex(b) for b in data]}")
        print(f"  seq_len={f['seq_len']}, seq_entries={len(f['seq'])}")
        print()

        # Hypothesis A: each entry is one bit (drop leading idle entry)
        a_bits = [lvl for lvl, _ in f['seq']]
        if a_bits and a_bits[0] == 1 and a_bits[1] == 0:
            # likely first entry is idle
            a_bits_trimmed = a_bits[1:]
        else:
            a_bits_trimmed = a_bits

        show("ours", ours)
        show("CTU (raw)", a_bits)
        show("CTU (no-idle)", a_bits_trimmed)

        # Hypothesis B: RLE, duration / 2000 = number of bits
        b_bits = []
        s = 0
        while s < len(f['seq']) and f['seq'][s][1] > 20000:
            s += 1
        for lvl, dur in f['seq'][s:]:
            n_bits = round(dur / 2000)
            b_bits.extend([lvl] * n_bits)
        show("CTU (RLE/2000)", b_bits)

        # Find first divergence
        ref, test = ours, b_bits
        first_diff = None
        for j in range(min(len(ref), len(test))):
            if ref[j] != test[j]:
                first_diff = j
                break
        if first_diff is not None:
            print(f"  First diff at bit {first_diff}")
            print(f"    ours[{first_diff-3}:{first_diff+4}] = {ours[max(0,first_diff-3):first_diff+4]}")
            print(f"    CTU [{first_diff-3}:{first_diff+4}] = {b_bits[max(0,first_diff-3):first_diff+4]}")
        else:
            print(f"  No divergence in first {min(len(ref), len(test))} bits")
        print()


if __name__ == "__main__":
    main()
