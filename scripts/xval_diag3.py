#!/usr/bin/env python3
"""Show raw vs stuffed vs CTU to find stuff-bit insertion points."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "tb"))

from can_fd_reference import generate_can_fd_frame, _raw_of, stuff_bits, dlc_len
from scripts.xval_ctu_parser import parse_vhdl_reference_data, filter_can_fd_base_frames


def show(name, bits, max_len=80):
    s = "".join(str(b) for b in bits[:max_len])
    print(f"  {name:20s} (len={len(bits):3d}): {s}{'...' if len(bits) > max_len else ''}")


def main():
    path = sys.argv[1]
    frames = filter_can_fd_base_frames(parse_vhdl_reference_data(path))

    for i, f in enumerate(frames[:2]):
        fr = f['frame']
        n = dlc_len(fr['dlc'])
        data = fr['data'][:n]
        
        raw = _raw_of(fr['identifier'], fr['dlc'], data, fr['brs'] == 1)
        stuffed, stuff_positions = stuff_bits(raw)
        ours = generate_can_fd_frame(fr['identifier'], fr['dlc'], data, fr['brs'] == 1)

        # CTU RLE
        ctu_bits = []
        s = 0
        while s < len(f['seq']) and f['seq'][s][1] > 20000:
            s += 1
        for lvl, dur in f['seq'][s:]:
            n_bits = round(dur / 2000)
            ctu_bits.extend([lvl] * n_bits)

        print(f"=== Frame {i}: ID={fr['identifier']:#05x} DLC={fr['dlc']} BRS={fr['brs']} ===")
        print(f"  Stuff positions (raw_idx, stuffed_idx, bit): {stuff_positions}")
        print()
        
        show("raw (no stuff)", raw)
        show("ours (stuffed)", ours)
        show("CTU (RLE/2000)", ctu_bits)
        print()

        # Find first divergence
        ref, test = ours, ctu_bits
        first_diff = None
        for j in range(min(len(ref), len(test))):
            if ref[j] != test[j]:
                first_diff = j
                break
        
        if first_diff is not None:
            print(f"  First diff at bit {first_diff}")
            start = max(0, first_diff - 10)
            end = min(len(ours), first_diff + 15)
            print(f"    ours[{start}:{end}] = {''.join(str(b) for b in ours[start:end])}")
            print(f"    CTU [{start}:{end}] = {''.join(str(b) for b in ctu_bits[start:end])}")
            
            # Check if diff is near a stuff position
            stuffed_indices = [sp[1] for sp in stuff_positions]
            near_stuff = [p for p in stuffed_indices if abs(p - first_diff) < 5]
            if near_stuff:
                print(f"    Near stuff positions: {near_stuff}")
            
            # Show more context around the diff
            print(f"\n  Extended context around bit {first_diff}:")
            start2 = max(0, first_diff - 5)
            end2 = min(min(len(ours), len(ctu_bits)), first_diff + 20)
            print(f"    ours: {''.join(str(b) for b in ours[start2:end2])}")
            print(f"    CTU:  {''.join(str(b) for b in ctu_bits[start2:end2])}")
            
            # Mark differences
            marker = ' ' * (first_diff - start2)
            marker += '^' * (end2 - first_diff)
            print(f"          {marker}")
        print()


if __name__ == "__main__":
    main()
