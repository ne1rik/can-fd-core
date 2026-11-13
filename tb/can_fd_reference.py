"""ISO 11898-1:2015 CAN FD reference model (FBFF, 11-bit ID).

Two CRC conventions coexist here on purpose:
  * calculate_crc()        -> pure catalogue algorithm, init = 0
                              (used by test_crc17 / test_crc21)
  * frame-level CRC        -> init = MSB set, computed over the dynamically
                              stuffed stream PLUS the 4-bit stuff count
                              (used by generate_can_fd_frame)

Frame boundary = end of EOF. The tail is 10 bits:
CRC delimiter + ACK slot + ACK delimiter + EOF x 7. No IFS is appended.
"""

# BRS position in the UNSTUFFED frame:
# SOF(1) + ID(11) + RRS,IDE,FDF,res(4) = 16
BRS_RAW_INDEX = 16


def dlc_len(d):
    """ISO DLC -> payload bytes mapping."""
    return d if d <= 8 else {9: 12, 10: 16, 11: 20, 12: 24,
                             13: 32, 14: 48, 15: 64}[d]


def stuff_bits(bits):
    """Dynamic bit stuffing. The inserted bit starts the next run.

    Returns (stuffed_bits, positions) where positions is a list of
    (raw_index, stuffed_index, stuff_bit).
    """
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


def calculate_crc(bitstream, payload_len_bytes):
    """Pure catalogue CRC (init = 0). Kept for algorithm-level tests."""
    w, poly = (21, 0x102899) if payload_len_bytes > 16 else (17, 0x1685B)
    m = (1 << w) - 1
    c = 0
    for b in bitstream:
        msb = (c >> (w - 1)) & 1
        c = (c << 1) & m
        if msb ^ b:
            c ^= poly
    return [(c >> i) & 1 for i in range(w - 1, -1, -1)]


def _crc_val(bits, w, poly, init):
    m = (1 << w) - 1
    c = init & m
    for b in bits:
        msb = (c >> (w - 1)) & 1
        c = (c << 1) & m
        if msb ^ b:
            c ^= poly
    return c


def _gray_sc(n):
    """Stuff count: 3-bit Gray code of (n mod 8) + even parity, MSB first."""
    n &= 7
    g = n ^ (n >> 1)
    p = ((g >> 2) ^ (g >> 1) ^ g) & 1
    return [(g >> 2) & 1, (g >> 1) & 1, g & 1, p]


def _raw_of(fid, dlc, data, brs):
    r = [0]
    r += [(fid >> i) & 1 for i in range(10, -1, -1)]
    r += [0, 0, 1, 0, 1 if brs else 0, 0]   # RRS,IDE,FDF,res,BRS,ESI
    r += [(dlc >> i) & 1 for i in range(3, -1, -1)]
    for by in data:
        r += [(by >> i) & 1 for i in range(7, -1, -1)]
    return r


def generate_can_fd_frame_ex(fid, dlc, data, brs=True):
    """Build a full ISO frame. Returns (bits, brs_index_in_stuffed_stream)."""
    raw = _raw_of(fid, dlc, data, brs)
    st, pos = stuff_bits(raw)

    # If the last dynamic stuff bit is triggered by the last raw bit, it
    # becomes the first fixed stuff bit of the CRC field.
    boundary = bool(pos) and pos[-1][0] == len(raw) - 1
    if boundary:
        fsb = st[-1]
        st = st[:-1]
        pos = pos[:-1]
    else:
        fsb = None

    sc = _gray_sc(len(pos))
    w, poly = (21, 0x102899) if dlc_len(dlc) > 16 else (17, 0x1685B)
    crc = _crc_val(st + sc, w, poly, 1 << (w - 1))
    cb = [(crc >> i) & 1 for i in range(w - 1, -1, -1)]

    # CRC field: leading FSB, then (SC + CRC) with an FSB before each
    # subsequent 4-bit group. Fixed stuff bits are NOT part of the CRC input.
    field = [fsb if boundary else 1 - (st[-1] if st else 0)]
    seq = sc + cb
    i = 0
    while i < len(seq):
        g = seq[i:i + 4]
        field += g
        i += 4
        if i < len(seq):
            field.append(1 - g[-1])

    bits = st + field + [1, 1, 1] + [1] * 7
    shift = sum(1 for (ri, _si, _sb) in pos if ri < BRS_RAW_INDEX)
    return bits, BRS_RAW_INDEX + shift


def generate_can_fd_frame(fid, dlc, data, brs=True):
    """Build a full ISO frame, returning only the bit list."""
    return generate_can_fd_frame_ex(fid, dlc, data, brs)[0]


if __name__ == "__main__":
    for name, fid, dlc, data in [("anchor 5AA/8/FF*8", 0x5AA, 8, [0xFF] * 8),
                                 ("123/9/AA*12", 0x123, 9, [0xAA] * 12),
                                 ("123/9/00*12", 0x123, 9, [0x00] * 12)]:
        bits, bi = generate_can_fd_frame_ex(fid, dlc, data, True)
        print(f"{name:22s} len={len(bits):4d} brs_index={bi}")


def frame_layout(fid, dlc, data, brs=True):
    """Full frame decomposition with bit indices, for checkers and injectors.

    Mirrors generate_can_fd_frame_ex. tests/test_model_conformance.py asserts
    that layout['bits'] == generate_can_fd_frame(...) so the two cannot drift.
    """
    raw = _raw_of(fid, dlc, data, brs)
    st, pos = stuff_bits(raw)

    boundary = bool(pos) and pos[-1][0] == len(raw) - 1
    if boundary:
        fsb = st[-1]
        st = st[:-1]
        pos = pos[:-1]
    else:
        fsb = None

    sc = _gray_sc(len(pos))
    w, poly = (21, 0x102899) if dlc_len(dlc) > 16 else (17, 0x1685B)
    crc = _crc_val(st + sc, w, poly, 1 << (w - 1))
    cb = [(crc >> i) & 1 for i in range(w - 1, -1, -1)]

    field = [fsb if boundary else 1 - (st[-1] if st else 0)]
    fsb_off = [0]
    seq = sc + cb
    i = 0
    while i < len(seq):
        g = seq[i:i + 4]
        field += g
        i += 4
        if i < len(seq):
            fsb_off.append(len(field))
            field.append(1 - g[-1])

    bits = st + field + [1, 1, 1] + [1] * 7
    shift = sum(1 for (ri, _si, _sb) in pos if ri < BRS_RAW_INDEX)

    seq_off = [k for k in range(len(field)) if k not in set(fsb_off)]
    base = len(st)

    return {
        "bits": bits,
        "brs_index": BRS_RAW_INDEX + shift,
        "raw_len": len(raw),
        "dyn_count": len(pos),
        "dyn_stuff_indices": [si for (_ri, si, _sb) in pos],
        "boundary_fsb": boundary,
        "stuffed_data_len": base,
        "crc_field_start": base,
        "crc_field_len": len(field),
        "fsb_indices": [base + k for k in fsb_off],
        "sc_indices": [base + k for k in seq_off[:4]],
        "crc_bit_indices": [base + k for k in seq_off[4:4 + w]],
        "tail_start": base + len(field),
        "tail_len": 10,
        "crc_width": w,
        "crc_value": crc,
        "stuff_count_bits": sc,
        "payload_bytes": dlc_len(dlc),
    }
