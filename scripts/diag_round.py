#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "tb"))

from can_fd_reference import generate_can_fd_frame, dlc_to_bytes
from scripts.xval_ctu_parser import parse_vhdl_reference_data, filter_can_fd_base_frames, strip_idle

def expand(seq, arbo_ns, fast_ns, fast_start, fast_end):
    bits = []
    for idx, (lvl, dur) in enumerate(seq):
        bit_ns = fast_ns if fast_start <= idx < fast_end else arbo_ns
        # Пробуем разные виды округления
        n = max(1, round(dur / bit_ns))
        bits.extend([lvl] * n)
    return bits

def main():
    vhd = sys.argv[1]
    frames = filter_can_fd_base_frames(parse_vhdl_reference_data(vhd))
    f = frames[0]
    fr = f['frame']
    n = dlc_to_bytes(fr['dlc'])
    ours = generate_can_fd_frame(fr['identifier'], fr['dlc'], fr['data'][:n], fr['brs'] == 1)
    real = strip_idle(f['seq'])

    print(f"Target len: {len(ours)}")
    # Перебираем базовые длительности и окна
    for arbo_ns in (2010, 2000, 1990):
        for fast_ns in (500, 510, 490):
            for i in range(len(real)):
                for j in range(i, len(real)+1):
                    bits = expand(real, arbo_ns, fast_ns, i, j)
                    if bits == ours:
                        print(f"EXACT MATCH: arbo={arbo_ns}ns, fast={fast_ns}ns, window=[{i},{j})")
                        return
    print("No exact match found with simple rounding. Needs deeper analysis.")

if __name__ == "__main__":
    main()
