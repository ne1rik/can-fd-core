#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "tb"))

from can_fd_reference import _raw_of, dlc_to_bytes
from scripts.xval_ctu_parser import parse_vhdl_reference_data, filter_can_fd_base_frames, strip_idle

def expand(seq, bit_ns):
    bits = []
    for lvl, dur in seq:
        n = max(1, round(dur / bit_ns)) # Гарантируем хотя бы 1 бит
        bits.extend([lvl] * n)
    return bits

def main():
    vhd = sys.argv[1]
    frames = filter_can_fd_base_frames(parse_vhdl_reference_data(vhd))
    f = frames[0] # Берем только первый кадр для анализа
    fr = f['frame']
    n = dlc_to_bytes(fr['dlc'])
    raw = _raw_of(fr['identifier'], fr['dlc'], fr['data'][:n], fr['brs'] == 1)
    real_seq = strip_idle(f['seq'])

    print(f"=== Frame 0: ID={fr['identifier']:#x} DLC={fr['dlc']} BRS={fr['brs']} ===")
    print(f"Raw (no stuff) len: {len(raw)}")
    print(f"Raw bits:  {''.join(map(str, raw[:60]))}...")
    print(f"\nSeq entries ({len(real_seq)}):")
    for i, (lvl, dur) in enumerate(real_seq[:15]):
        print(f"  [{i:2d}] ({lvl}, {dur:5d} ns)")

    # Пробуем разные длительности бита
    for ns in (2010, 2000, 1990, 1000, 500):
        expanded = expand(real_seq, ns)
        # Обрезаем/дополняем для сравнения с raw
        min_len = min(len(raw), len(expanded))
        diffs = [k for k in range(min_len) if raw[k] != expanded[k]]
        print(f"\n--- Expand with {ns} ns/bit ---")
        print(f"Len: {len(expanded)}, First 60 bits: {''.join(map(str, expanded[:60]))}...")
        if diffs:
            print(f"First diff vs raw at bit {diffs[0]}")
        else:
            print("Matches raw in first", min_len, "bits!")

if __name__ == "__main__":
    main()
