#!/usr/bin/env python3
"""Diagnostic: decode CTU seq (BRS=0 only) and compare to our model.

No model changes. Reports exact / prefix / mismatch stats and first diffs.
"""
import re, sys
from pathlib import Path
from collections import Counter
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT/"tb"))
from can_fd_reference import generate_can_fd_frame, dlc_len

def tuples(text):
    m = re.search(r'constant\s+C_reference_data_set_\d+\s*:\s*t_reference_data_set\s*:=\s*\(', text)
    if not m: return
    pos = m.end()
    while pos < len(text):
        while pos < len(text) and text[pos] in " \t\n\r,": pos += 1
        if pos >= len(text) or text[pos] == ')': return
        if text[pos] != '(': pos += 1; continue
        depth=0; start=pos; j=pos
        while j < len(text):
            if text[j]=='(': depth+=1
            elif text[j]==')':
                depth-=1
                if depth==0: break
            j+=1
        if depth: return
        yield text[start:j+1]; pos=j+1

def fields(t):
    head = t.split('seq =>',1)[0]
    def b(n):
        m=re.search(rf"{n}\s*=>\s*'([01])'",head); return int(m.group(1)) if m else None
    d=re.search(r'dlc\s*=>\s*"([01]{4})"',head)
    i=re.search(r'identifier\s*=>\s*(\d+)',head)
    dm=re.search(r'data\s*=>\s*\((.*?)\)',head,re.DOTALL)
    data=[int(h,16) for h in re.findall(r'x"([0-9a-fA-F]{2})"',dm.group(1))] if dm else []
    seqpart=t.split('seq =>',1)[1]
    seq=[(int(a),int(b)) for a,b in re.findall(r"\('([01])',\s*(\d+)\s*ns\)",seqpart)]
    return dict(ff=b('frame_format'),it=b('ident_type'),rtr=b('rtr'),brs=b('brs'),
                esi=b('esi'),erf=b('erf'),dlc=int(d.group(1),2) if d else None,
                id=int(i.group(1)) if i else None,data=data), seq

def expand(seq, bit_ns=2000, idle=20000):
    s=0
    while s<len(seq) and seq[s][0]==1 and seq[s][1]>idle: s+=1
    e=len(seq)
    while e>s and seq[e-1][0]==1 and seq[e-1][1]>idle: e-=1
    bits=[]
    for lvl,dur in seq[s:e]:
        bits.extend([lvl]*max(1,round(dur/bit_ns)))
    return bits

def prefix_match(a, b):
    """Return length of common prefix."""
    i = 0
    for x, y in zip(a, b):
        if x != y: break
        i += 1
    return i

def main():
    path=Path(sys.argv[1]); stats=Counter(); diffs=[]
    for t in tuples(path.read_text()):
        f,seq=fields(t)
        if not(f['ff']==1 and f['it']==0 and f['rtr']==0 and f['erf']==0 and f['esi']==0 and f['brs']==0):
            continue
        n=dlc_len(f['dlc']); data=(f['data']+[0]*n)[:n]
        ours=generate_can_fd_frame(f['id'],f['dlc'],data,False)
        ctu=expand(seq)
        common = prefix_match(ctu, ours)
        if ctu==ours: stats['exact']+=1
        elif common == len(ctu): stats['ctu_prefix']+=1
        elif common == len(ours): stats['ours_prefix']+=1
        else:
            stats['mismatch']+=1
            k = common
            if len(diffs)<10:
                diffs.append((f['id'],f['dlc'],len(ctu),len(ours),k,
                              ''.join(map(str,ctu[max(0,k-6):k+8])),
                              ''.join(map(str,ours[max(0,k-6):k+8]))))
    print("BRS=0 waveform diag:",dict(stats))
    for d in diffs:
        print(f"  id={d[0]:#05x} dlc={d[1]} ctu={d[2]} ours={d[3]} first_diff={d[4]}\n    ctu:{d[5]}\n    our:{d[6]}")

if __name__=="__main__": main()
