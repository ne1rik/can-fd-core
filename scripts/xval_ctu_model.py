#!/usr/bin/env python3
"""Cross-validate CTU frame metadata against our reference model.

For each CTU vector: generate a frame with our model, then DECODE it back
independently (strip dynamic stuff bits, parse fields) and compare all five
aspects: ID, DLC, data, BRS, and structural validity.
"""
import json, sys
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tb"))

from can_fd_reference import generate_can_fd_frame, frame_layout, dlc_len


def decode_back(bits, lay):
    """Recover fields from our own frame by removing dynamic stuff bits."""
    stuff = set(lay["dyn_stuff_indices"])
    raw = [b for i, b in enumerate(bits[:lay["stuffed_data_len"]]) if i not in stuff]
    fid = 0
    for b in raw[1:12]:
        fid = (fid << 1) | b
    brs = raw[16]
    dlc = 0
    for b in raw[18:22]:
        dlc = (dlc << 1) | b
    n = dlc_len(dlc)
    data = []
    for k in range(n):
        v = 0
        for b in raw[22 + 8*k : 30 + 8*k]:
            v = (v << 1) | b
        data.append(v)
    return {"id": fid, "dlc": dlc, "data": data, "brs": brs, "sof": raw[0]}


def main():
    vectors = json.loads((ROOT / "coverage/ctu_vectors.json").read_text())
    print(f"vectors: {len(vectors)}")
    fails = []
    stats = Counter()

    for i, v in enumerate(vectors):
        fid, dlc, brs = v["id"], v["dlc"], bool(v["brs"])
        n = dlc_len(dlc)
        data = (v["data"] + [0]*n)[:n]
        tag = f"vec{i} id={fid:#05x} dlc={dlc} brs={int(brs)}"

        try:
            bits = generate_can_fd_frame(fid, dlc, data, brs)
            lay = frame_layout(fid, dlc, data, brs)
        except Exception as e:
            fails.append((tag, f"model raised {e}")); continue

        # aspect 5: structural validity
        if lay["bits"] != bits:
            fails.append((tag, "layout/generator disagree")); continue
        if len(bits) != lay["stuffed_data_len"] + lay["crc_field_len"] + 10:
            fails.append((tag, "geometry")); continue
        if bits[-10:] != [1]*10:
            fails.append((tag, "tail not 10 recessive")); continue
        run = 1
        st = bits[:lay["stuffed_data_len"]]
        bad = False
        for a, b in zip(st, st[1:]):
            run = run + 1 if a == b else 1
            if run > 5: bad = True; break
        if bad:
            fails.append((tag, "six-bit run in stuffed region")); continue
        if lay["crc_width"] != (21 if n > 16 else 17):
            fails.append((tag, "wrong CRC width")); continue

        # aspects 1-4: decoded fields
        got = decode_back(bits, lay)
        if got["sof"] != 0:      fails.append((tag, "SOF not dominant")); continue
        if got["id"] != fid:     fails.append((tag, f"ID {got['id']:#x}")); continue
        if got["dlc"] != dlc:    fails.append((tag, f"DLC {got['dlc']}")); continue
        if got["data"] != data:  fails.append((tag, "data mismatch")); continue
        if got["brs"] != int(brs): fails.append((tag, f"BRS {got['brs']}")); continue
        if bits[lay["brs_index"]] != int(brs):
            fails.append((tag, "BRS bit on wire")); continue

        stats["pass"] += 1
        stats[f"dlc{dlc}"] += 1
        stats[f"brs{int(brs)}"] += 1

    print(f"PASS {stats['pass']}/{len(vectors)}")
    if fails:
        print(f"\nFAILURES ({len(fails)}), first 20:")
        for tag, why in fails[:20]:
            print(f"  {tag}: {why}")
        return 1
    print("all five aspects match on every CTU vector")
    return 0


if __name__ == "__main__":
    sys.exit(main())
