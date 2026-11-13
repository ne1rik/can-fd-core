#!/usr/bin/env python3
"""Bit-exact check of our FEFF (29-bit) model against CTU extended frames.

Same ACK-only-difference criterion as the FBFF check. If the header layout is
wrong (e.g. the reserved bit does not exist in FEFF), this reports early
first-diff positions instead of ACK_ONLY_DIFF.
"""
import sys
from pathlib import Path
from collections import Counter
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT/"tb"))
sys.path.insert(0, str(ROOT/"scripts"))
from can_fd_reference import generate_can_fd_frame, dlc_len
from xval_ctu_wave_diag import tuples, fields, expand

def main():
    stats = Counter(); bad = []
    for t in tuples(Path(sys.argv[1]).read_text()):
        f, seq = fields(t)
        if not (f['ff']==1 and f['it']==1 and f['rtr']==0
                and f['erf']==0 and f['esi']==0 and f['brs']==0):
            continue
        n = dlc_len(f['dlc']); data = (f['data']+[0]*n)[:n]
        ours = generate_can_fd_frame(f['id'], f['dlc'], data, False, extended=True)
        ctu = expand(seq)
        L = len(ours)
        if len(ctu) < L:
            stats['ctu_shorter'] += 1; continue
        pre = L - 9
        if ctu[:pre] != ours[:pre]:
            k = next(i for i,(a,b) in enumerate(zip(ctu[:pre], ours[:pre])) if a!=b)
            stats['prefix_mismatch'] += 1
            if len(bad) < 6:
                bad.append((f['id'], f['dlc'], L, k,
                            ''.join(map(str,ctu[max(0,k-8):k+10])),
                            ''.join(map(str,ours[max(0,k-8):k+10]))))
            continue
        if ctu[pre] != 0 or ours[pre] != 1:
            stats['ack_unexpected'] += 1; continue
        if any(b != 1 for b in ctu[pre+1:]):
            stats['tail_not_idle'] += 1; continue
        stats['ACK_ONLY_DIFF'] += 1
    print("FEFF:", dict(stats))
    for b in bad:
        print(f"  id={b[0]:#011x} dlc={b[1]} ours_len={b[2]} first_diff={b[3]}\n    ctu:{b[4]}\n    our:{b[5]}")

if __name__ == "__main__":
    main()
