#!/usr/bin/env python3
"""Bit-exact check of our Classic CAN model against CTU classical frames.

Criterion identical to the FD checks: everything up to and including the CRC
delimiter must match; the ACK slot differs (CTU receiver drives dominant);
everything after is recessive idle padding.
"""
import sys
from pathlib import Path
from collections import Counter
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT/"tb"))
sys.path.insert(0, str(ROOT/"scripts"))
from can_fd_reference import generate_can_fd_frame, dlc_len
from xval_ctu_wave_diag import tuples, fields, expand

def check(f, seq, extended):
    n = dlc_len(f['dlc'], classic=True)
    data = (f['data'] + [0]*n)[:n]
    ours = generate_can_fd_frame(f['id'], f['dlc'], data, False,
                                 extended=extended, classic=True)
    ctu = expand(seq)
    L = len(ours)
    if len(ctu) < L:
        return 'ctu_shorter', None
    pre = L - 9
    if ctu[:pre] != ours[:pre]:
        k = next(i for i,(a,b) in enumerate(zip(ctu[:pre], ours[:pre])) if a!=b)
        return 'prefix_mismatch', (f['id'], f['dlc'], L, len(ctu), k,
                                   ''.join(map(str,ctu[max(0,k-8):k+10])),
                                   ''.join(map(str,ours[max(0,k-8):k+10])))
    if ctu[pre] != 0 or ours[pre] != 1:
        return 'ack_unexpected', None
    if any(b != 1 for b in ctu[pre+1:]):
        return 'tail_not_idle', None
    return 'ACK_ONLY_DIFF', None

def main():
    stats = Counter(); bad = []
    for t in tuples(Path(sys.argv[1]).read_text()):
        f, seq = fields(t)
        if not (f['ff'] == 0 and f['rtr'] == 0 and f['erf'] == 0 and f['esi'] == 0):
            continue
        ext = (f['it'] == 1)
        kind, info = check(f, seq, ext)
        stats[('ext' if ext else 'base') + ':' + kind] += 1
        if info and len(bad) < 6:
            bad.append(('ext' if ext else 'base', info))
    print("Classic CAN:", dict(stats))
    for tag, b in bad:
        print(f"  [{tag}] id={b[0]:#x} dlc={b[1]} ours={b[2]} ctu={b[3]} first_diff={b[4]}\n"
              f"    ctu:{b[5]}\n    our:{b[6]}")

if __name__ == "__main__":
    main()
