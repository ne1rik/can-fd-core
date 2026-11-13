#!/usr/bin/env python3
"""Decisive check: is the only frame-region difference the receiver-driven ACK?

Hypothesis: our frame matches CTU bit-for-bit up to and including the CRC
delimiter; the ACK slot differs (CTU=0 driven by receiver, ours=1 unacked);
everything after is recessive on both sides (ACK del + EOF + idle padding).
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
        if not (f['ff']==1 and f['it']==0 and f['rtr']==0
                and f['erf']==0 and f['esi']==0 and f['brs']==0):
            continue
        n = dlc_len(f['dlc']); data = (f['data']+[0]*n)[:n]
        ours = generate_can_fd_frame(f['id'], f['dlc'], data, False)
        ctu = expand(seq)
        L = len(ours)
        if len(ctu) < L:
            stats['ctu_shorter'] += 1; continue

        # 1) everything before the ACK slot must match exactly
        pre = L - 9                      # ACK slot index
        if ctu[:pre] != ours[:pre]:
            k = next(i for i,(a,b) in enumerate(zip(ctu[:pre], ours[:pre])) if a!=b)
            stats['prefix_mismatch'] += 1
            if len(bad) < 8: bad.append((f['id'], f['dlc'], 'prefix', k))
            continue

        # 2) ACK slot: CTU dominant, ours recessive
        if ctu[pre] != 0 or ours[pre] != 1:
            stats['ack_unexpected'] += 1
            if len(bad) < 8: bad.append((f['id'], f['dlc'], f"ack ctu={ctu[pre]} our={ours[pre]}", pre))
            continue

        # 3) after ACK: both recessive (ACK del + EOF), CTU tail is idle padding
        if ours[pre+1:] != [1]*(L-pre-1):
            stats['our_tail_not_recessive'] += 1; continue
        if any(b != 1 for b in ctu[pre+1:L]):
            stats['ctu_tail_not_recessive'] += 1
            if len(bad) < 8: bad.append((f['id'], f['dlc'], 'ctu tail', pre+1))
            continue
        if any(b != 1 for b in ctu[L:]):
            stats['padding_not_idle'] += 1; continue

        stats['ACK_ONLY_DIFF'] += 1

    print("result:", dict(stats))
    for b in bad: print("  ", b)

if __name__ == "__main__":
    main()
