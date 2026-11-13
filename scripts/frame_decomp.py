"""Field-by-field decomposition of an ISO 11898-1:2015 FBFF frame.

Purpose: make frame-length disagreements diagnosable. Both reference
implementations must print the same raw / stuffed / FSB / field / tail
numbers before any length is treated as an anchor.

Usage: python3 scripts/frame_decomp.py
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tb"))
from can_fd_reference import generate_can_fd_frame, dlc_len  # noqa: E402


def raw_of(fid, dlc, data, brs):
    r = [0]
    r += [(fid >> i) & 1 for i in range(10, -1, -1)]
    r += [0, 0, 1, 0, 1 if brs else 0, 0]
    r += [(dlc >> i) & 1 for i in range(3, -1, -1)]
    for by in data:
        r += [(by >> i) & 1 for i in range(7, -1, -1)]
    return r


def stuff(bits):
    out, pos = [], []
    last, run = None, 0
    for i, b in enumerate(bits):
        out.append(b)
        if b == last:
            run += 1
        else:
            last, run = b, 1
        if run == 5:
            sb = 1 - b
            out.append(sb)
            pos.append((i, len(out) - 1, sb))
            last, run = sb, 1
    return out, pos


def decompose(name, fid, dlc, data, brs):
    raw = raw_of(fid, dlc, data, brs)
    st, pos = stuff(raw)
    boundary = bool(pos) and pos[-1][0] == len(raw) - 1
    if boundary:
        st = st[:-1]
        pos = pos[:-1]
    frame = generate_can_fd_frame(fid, dlc, list(data), bool(brs))
    w = 21 if dlc_len(dlc) > 16 else 17
    seq_len = 4 + w
    groups = (seq_len + 3) // 4
    fsb = 1 + (groups - 1)
    field = fsb + seq_len
    tail = len(frame) - len(st) - field
    print(f"--- {name} ---")
    print(f"  CTRL width      : 6 (RRS,IDE,FDF,res,BRS,ESI)")
    print(f"  raw             : {len(raw)}")
    print(f"  stuffed         : {len(st)}   dyn_stuff={len(pos)}  boundary={boundary}")
    print(f"  CRC width       : {w}")
    print(f"  FSB count       : {fsb}")
    print(f"  field           : {field}  (= FSB {fsb} + SC 4 + CRC {w})")
    print(f"  tail            : {tail}  (CRC_delim 1 + ACK_slot 1 + ACK_delim 1 + EOF 7)")
    print(f"  TOTAL           : {len(frame)}")
    print(f"  last 16 bits    : {''.join(map(str, frame[-16:]))}")
    print(f"  BRS (raw idx16) : {raw[16]}  (1 = recessive = second bit rate)")
    print()


if __name__ == "__main__":
    decompose("anchor 0x5AA / DLC8 / 8x0xFF", 0x5AA, 8, [0xFF] * 8, True)
    decompose("0x123 / DLC9 / 12x0xAA", 0x123, 9, [0xAA] * 12, True)
    decompose("0x123 / DLC9 / 12x0x00", 0x123, 9, [0x00] * 12, True)
