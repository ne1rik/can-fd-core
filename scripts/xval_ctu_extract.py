#!/usr/bin/env python3
"""Extract CTU reference frame metadata (ignores seq waveform).

Scope: ISO CAN FD base (11-bit) data frames, no error injection, ESI=0.
Outputs JSON vectors + prints stats. Does NOT touch the reference model.
"""
import json, re, sys
from pathlib import Path

REF_DIR = Path.home() / "ctu-can-fd-ref/test/main_tb/reference_test_data_sets"

def parse_frames(path):
    text = path.read_text()
    # split into per-record chunks between 'frame =>' and 'seq =>'
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
        out.append({
            "frame_format": bit("frame_format"),
            "ident_type": bit("ident_type"),
            "rtr": bit("rtr"),
            "brs": bit("brs"),
            "esi": bit("esi"),
            "erf": bit("erf"),
            "dlc": int(dlc_m.group(1),2) if dlc_m else None,
            "id": num("identifier"),
            "data": data,
        })
    return out

def in_scope(f):
    return (f["frame_format"]==1 and f["ident_type"]==0 and f["rtr"]==0
            and f["erf"]==0 and f["esi"]==0 and f["dlc"] is not None and f["id"] is not None)

def main():
    files = sorted(REF_DIR.glob("reference_data_set_*.vhd"))
    all_frames, scoped = [], []
    for p in files:
        fr = parse_frames(p)
        all_frames += fr
        scoped += [f for f in fr if in_scope(f)]
    print(f"files: {len(files)}")
    print(f"total frames: {len(all_frames)}")
    print(f"in-scope (FD base, data, erf=0, esi=0): {len(scoped)}")
    from collections import Counter
    print("DLC histogram:", dict(sorted(Counter(f['dlc'] for f in scoped).items())))
    print("BRS histogram:", dict(Counter(f['brs'] for f in scoped)))
    out = Path("coverage/ctu_vectors.json")
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(scoped, indent=1))
    print(f"wrote {out}")

if __name__ == "__main__":
    main()
