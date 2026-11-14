#!/usr/bin/env python3
"""Extract ALL valid CTU reference frame metadata (FD + Classic, Base + Ext).

Scope: data frames (rtr=0), no injected error (erf=0), ESI=0.
Outputs JSON with explicit 'format' field for downstream parameterized testing.
"""
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REF_DIR = ROOT.parent / "ctu-can-fd-ref/test/main_tb/reference_test_data_sets"
OUT_FILE = ROOT / "coverage/ctu_vectors_all.json"

def parse_frames(path):
    text = path.read_text()
    chunks = re.split(r'\bframe\s*=>', text)[1:]
    out = []
    for ch in chunks:
        head = ch.split('seq =>', 1)[0]
        def bit(name):
            m = re.search(rf"{name}\s*=>\s*'([01])'", head)
            return int(m.group(1)) if m else None
        def num(name):
            m = re.search(rf"{name}\s*=>\s*(\d+)", head)
            return int(m.group(1)) if m else None
        dlc_m = re.search(r'dlc\s*=>\s*"([01]{4})"', head)
        data_m = re.search(r'data\s*=>\s*\((.*?)\)', head, re.DOTALL)
        data = [int(h,16) for h in re.findall(r'x"([0-9a-fA-F]{2})"', data_m.group(1))] if data_m else []
        
        ff = bit("frame_format")
        it = bit("ident_type")
        if ff is None or dlc_m is None:
            continue
            
        fmt = "fd_ext" if ff == 1 and it == 1 else \
              "fd_base" if ff == 1 and it == 0 else \
              "classic_ext" if ff == 0 and it == 1 else "classic_base"
              
        out.append({
            "format": fmt,
            "frame_format": ff,
            "ident_type": it,
            "rtr": bit("rtr"),
            "brs": bit("brs"),
            "esi": bit("esi"),
            "erf": bit("erf"),
            "dlc": int(dlc_m.group(1), 2),
            "id": num("identifier"),
            "data": data,
        })
    return out

def main():
    files = sorted(REF_DIR.glob("reference_data_set_*.vhd"))
    all_frames = []
    for p in files:
        all_frames += parse_frames(p)
    
    # Filter to valid scope: rtr=0, erf=0, esi=0
    valid_frames = [f for f in all_frames if f["rtr"] == 0 and f["erf"] == 0 and f["esi"] == 0]
    
    OUT_FILE.parent.mkdir(exist_ok=True)
    OUT_FILE.write_text(json.dumps(valid_frames, indent=1))
    
    from collections import Counter
    counts = Counter(f["format"] for f in valid_frames)
    print(f"Total valid frames: {len(valid_frames)}")
    for fmt, cnt in sorted(counts.items()):
        print(f"  {fmt:12s}: {cnt}")
    print(f"Wrote {OUT_FILE}")

if __name__ == "__main__":
    main()
