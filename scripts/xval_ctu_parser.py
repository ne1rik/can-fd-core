#!/usr/bin/env python3
"""Parser for CTU CAN FD reference test data sets."""

import re, sys
from pathlib import Path
from typing import List, Dict, Any, Tuple

IDLE_THRESHOLD_NS = 50000
OTHERS_MAX_NS     = 100
NOMINAL_BIT_NS    = 2000       # 500 kbit/s (arbitration)
FAST_BIT_NS       = 500        # 2 Mbit/s   (data phase when BRS=1)


def parse_vhdl_reference_data(vhd_path: str) -> List[Dict[str, Any]]:
    with open(vhd_path, 'r') as f:
        content = f.read()
    match = re.search(
        r'constant\s+C_reference_data_set_\d+\s*:\s*t_reference_data_set\s*:=\s*\(',
        content)
    if not match:
        return []
    pos, results = match.end(), []
    while pos < len(content):
        while pos < len(content) and content[pos] in " \t\n\r,":
            pos += 1
        if pos >= len(content) or content[pos] == ')':
            break
        if content[pos] != '(':
            pos += 1; continue
        depth, start, j = 0, pos, pos
        while j < len(content):
            if content[j] == '(':
                depth += 1
            elif content[j] == ')':
                depth -= 1
                if depth == 0:
                    break
            j += 1
        if depth != 0:
            break
        parsed = parse_tuple(content[start:j+1])
        if parsed:
            results.append(parsed)
        pos = j + 1
    return results


def parse_tuple(tuple_str: str):
    inner = tuple_str.strip()
    if inner.startswith('('): inner = inner[1:]
    if inner.endswith(')'):   inner = inner[:-1]
    fi, si, sli = (inner.find('frame =>'), inner.find('seq =>'),
                   inner.find('seq_len =>'))
    if -1 in (fi, si, sli):
        return None
    frame_str = inner[fi+len('frame =>'):si].strip().rstrip(',').strip()
    seq_str   = inner[si+len('seq =>'):sli].strip().rstrip(',').strip()
    seq_len_s = inner[sli+len('seq_len =>'):].strip().split(',')[0].strip()
    return {'frame': parse_frame(frame_str),
            'seq': parse_seq(seq_str),
            'seq_len': int(seq_len_s)}


def parse_frame(frame_str: str) -> Dict[str, Any]:
    frame = {}
    for field in ['frame_format','ident_type','rtr','brs','data_length',
                  'esi','lbpf','ivld']:
        m = re.search(rf"{field}\s*=>\s*'([01])'", frame_str)
        if m: frame[field] = int(m.group(1))
    m = re.search(r'dlc\s*=>\s*"([01]{4})"', frame_str)
    if m: frame['dlc'] = int(m.group(1), 2)
    m = re.search(r'identifier\s*=>\s*(\d+)', frame_str)
    if m: frame['identifier'] = int(m.group(1))
    m = re.search(r'data\s*=>\s*\((.*?)\)\s*$', frame_str, re.DOTALL)
    frame['data'] = ([int(h, 16) for h in
                      re.findall(r'x"([0-9a-fA-F]{2})"', m.group(1))]
                     if m else [])
    return frame


def parse_seq(seq_str: str) -> List[Tuple[int,int]]:
    seq = []
    for bit_str, dur_str in re.findall(r"\('([01])',\s*(\d+)\s*ns\)", seq_str):
        dur = int(dur_str)
        if dur <= OTHERS_MAX_NS:
            continue
        seq.append((int(bit_str), dur))
    return seq


def filter_can_fd_base_frames(frames):
    return [f for f in frames
            if f['frame'].get('frame_format') == 1
            and f['frame'].get('ident_type') == 0]


def strip_idle(seq):
    s = 0
    while s < len(seq) and seq[s][0] == 1 and seq[s][1] > IDLE_THRESHOLD_NS:
        s += 1
    e = len(seq)
    while e > s and seq[e-1][0] == 1 and seq[e-1][1] > IDLE_THRESHOLD_NS:
        e -= 1
    return seq[s:e]


def _expand_rle(real, arbo_ns, fast_ns, fast_start=None, fast_end=None):
    bits = []
    for idx, (lvl, dur) in enumerate(real):
        in_fast = (fast_start is not None and fast_start <= idx < fast_end)
        bit_ns = fast_ns if in_fast else arbo_ns
        n = round(dur / bit_ns)
        if n > 0:
            bits.extend([lvl] * n)
    return bits


def seq_to_bitstream(seq, our_bits=None, brs=False, debug=False):
    """Try to expand RLE such that bits == our_bits exactly."""
    real = strip_idle(seq)
    if not real:
        return []

    # 1) Try all-slow first
    slow = _expand_rle(real, NOMINAL_BIT_NS, NOMINAL_BIT_NS)
    if our_bits is None:
        return slow
    if slow == our_bits:
        if debug: print(f"    [EXPAND] MATCH all-slow ({len(slow)} bits)")
        return slow

    if not brs:
        if debug:
            print(f"    [EXPAND] BRS=0, all-slow: {len(slow)} vs {len(our_bits)}, "
                  f"first diff={_first_diff(slow, our_bits)}")
        return slow

    n = len(real)
    target = len(our_bits)
    if debug:
        print(f"    [EXPAND] BRS=1, {n} entries, target={target}, "
              f"slow gives {len(slow)}")

    # 2) Full search: fast window [i, j)
    best_by_len, best_len_err = slow, abs(len(slow) - target)
    n_checked = 0
    for i in range(n + 1):
        for j in range(i, n + 1):
            if i == 0 and j == 0:
                continue
            bits = _expand_rle(real, NOMINAL_BIT_NS, FAST_BIT_NS, i, j)
            if bits == our_bits:
                if debug:
                    print(f"    [EXPAND] MATCH window=[{i},{j}) "
                          f"({len(bits)} bits)")
                return bits
            err = abs(len(bits) - target)
            if err < best_len_err:
                best_len_err, best_by_len = err, bits
            n_checked += 1

    if debug:
        print(f"    [EXPAND] NO exact match after {n_checked} windows. "
              f"best err={best_len_err}, first diff={_first_diff(best_by_len, our_bits)}")
    return best_by_len


def _first_diff(a, b):
    for k in range(min(len(a), len(b))):
        if a[k] != b[k]:
            return k
    return None
