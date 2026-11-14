"""ISO 11898-1:2015 CAN/CAN FD reference model.

Formats:
  * FBFF (CAN FD, 11-bit ID, default)
  * FEFF (CAN FD, 29-bit ID, extended=True)
  * Classic CAN Base (classic=True, extended=False)
  * Classic CAN Extended (classic=True, extended=True)

CRC conventions:
  * catalogue CRC (init=0): calculate_crc() for FD, calculate_crc_classic() for Classic
  * frame-level CRC: init=MSB for FD, init=0 for Classic

Frame boundary = end of EOF. Tail is 10 bits:
CRC delimiter + ACK slot + ACK delimiter + EOF x 7.

Classic CAN note: CRC-15 is computed over the UNSTUFFED stream (header + data),
then appended, and the ENTIRE sequence (header + data + CRC) is then stuffed.
This differs from CAN FD where CRC is computed over the stuffed stream.
"""

# BRS position in UNSTUFFED header (FD only)
BRS_RAW_INDEX = 16       # FBFF: SOF(1) + ID(11) + RRS,IDE,FDF,res(4)
BRS_RAW_INDEX_EXT = 35   # FEFF: SOF(1) + IDA(11) + SRR,IDE(2) + IDB(18) + RRS,FDF,res(3)

HEADER_LEN = 22          # FBFF: 16 + BRS,ESI(2) + DLC(4)
HEADER_LEN_EXT = 41      # FEFF: 35 + BRS,ESI(2) + DLC(4)
HEADER_LEN_CLASSIC = 19  # Classic Base: SOF(1)+ID(11)+RTR,IDE,r0(3)+DLC(4)
HEADER_LEN_CLASSIC_EXT = 39  # Classic Ext: SOF(1)+IDA(11)+SRR,IDE(2)+IDB(18)+RTR,r1,r0(3)+DLC(4)


def dlc_len(d, classic=False):
    """ISO DLC -> payload bytes mapping."""
    if classic:
        return d if d <= 8 else 8  # Classic CAN max 8 bytes
    return d if d <= 8 else {9: 12, 10: 16, 11: 20, 12: 24,
                             13: 32, 14: 48, 15: 64}[d]


def stuff_bits(bits):
    """Dynamic bit stuffing. The inserted bit starts the next run.

    Returns (stuffed_bits, positions) with positions as
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


def _crc_val(bits, width, poly, init):
    """Bit-serial CRC, feedback = MSB xor data_bit, shift in zero."""
    mask = (1 << width) - 1
    crc = init
    for b in bits:
        fb = ((crc >> (width - 1)) & 1) ^ b
        crc = (crc << 1) & mask
        if fb:
            crc ^= poly
    return crc


def calculate_crc(bitstream, payload_len_bytes):
    """Catalogue CRC for CAN FD (init = 0). Returns CRC bits, MSB first."""
    w, poly = (21, 0x102899) if payload_len_bytes > 16 else (17, 0x1685B)
    v = _crc_val(bitstream, w, poly, 0)
    return [(v >> i) & 1 for i in range(w - 1, -1, -1)]


def calculate_crc_classic(bitstream):
    """Catalogue CRC-15 for Classic CAN (init = 0, poly = 0x4599)."""
    v = _crc_val(bitstream, 15, 0x4599, 0)
    return [(v >> i) & 1 for i in range(14, -1, -1)]


def _gray_sc(n):
    """Stuff count: 3-bit Gray of (n mod 8), MSB first, + even parity bit."""
    g = (n % 8) ^ ((n % 8) >> 1)
    bits = [(g >> i) & 1 for i in (2, 1, 0)]
    bits.append(sum(bits) % 2)
    return bits


def _raw_of(fid, dlc, data, brs, extended=False, classic=False):
    """Unstuffed header + payload (no CRC, no tail)."""
    n = dlc_len(dlc, classic)
    r = [0]  # SOF
    
    if classic:
        # Classic CAN 2.0
        if extended:
            # Extended frame
            r += [(fid >> i) & 1 for i in range(28, 17, -1)]  # ID A[28:18]
            r += [1, 1]  # SRR, IDE
            r += [(fid >> i) & 1 for i in range(17, -1, -1)]  # ID B[17:0]
            r += [0, 0, 0]  # RTR=0, r1=0, r0=0
        else:
            # Base frame
            r += [(fid >> i) & 1 for i in range(10, -1, -1)]  # ID[10:0]
            r += [0, 0, 0]  # RTR=0, IDE=0, r0=0
    else:
        # CAN FD
        if extended:
            r += [(fid >> i) & 1 for i in range(28, 17, -1)]  # ID A[28:18]
            r += [1, 1]  # SRR, IDE
            r += [(fid >> i) & 1 for i in range(17, -1, -1)]  # ID B[17:0]
            r += [0, 1, 0]  # RRS=0, FDF=1, res=0
        else:
            r += [(fid >> i) & 1 for i in range(10, -1, -1)]  # ID[10:0]
            r += [0, 0, 1, 0]  # RRS=0, IDE=0, FDF=1, res=0
        r += [1 if brs else 0, 0]  # BRS, ESI
    
    r += [(dlc >> i) & 1 for i in range(3, -1, -1)]  # DLC
    for k in range(n):
        v = data[k] if k < len(data) else 0
        r += [(v >> i) & 1 for i in range(7, -1, -1)]
    return r


def _build(fid, dlc, data, brs=True, extended=False, classic=False):
    """Full frame decomposition with bit indices."""
    raw = _raw_of(fid, dlc, data, brs, extended, classic)

    if classic:
        # Classic CAN: CRC is calculated over the UNSTUFFED stream.
        # Then CRC is appended, and the ENTIRE sequence is stuffed.
        crc = _crc_val(raw, 15, 0x4599, 0)
        cb = [(crc >> i) & 1 for i in range(14, -1, -1)]
        raw_with_crc = raw + cb
        
        st, pos = stuff_bits(raw_with_crc)
        bits = st + [1, 1, 1] + [1] * 7  # Tail: CRC del(1), ACK(1), ACK del(1), EOF(7)
        
        base = len(st)
        return {
            "bits": bits,
            "brs_index": None,
            "raw_len": len(raw),
            "dyn_count": len(pos),
            "dyn_stuff_indices": [si for (_ri, si, _sb) in pos],
            "boundary_fsb": False,
            "stuffed_data_len": base,  # Now includes CRC in the stuffed region
            "crc_field_start": len(raw),
            "crc_field_len": 15,
            "fsb_indices": [],
            "sc_indices": [],
            "crc_bit_indices": list(range(len(raw), len(raw) + 15)),
            "tail_start": base,
            "tail_len": 10,
            "crc_width": 15,
            "crc_value": crc,
            "stuff_count_bits": [],
            "payload_bytes": dlc_len(dlc, classic),
            "extended": extended,
            "classic": True,
            "header_len": HEADER_LEN_CLASSIC_EXT if extended else HEADER_LEN_CLASSIC,
        }
    else:
        # CAN FD: SBC + FSB
        st, pos = stuff_bits(raw)

        boundary = bool(pos) and pos[-1][0] == len(raw) - 1
        if boundary:
            fsb = st[-1]
            st = st[:-1]
            pos = pos[:-1]
        else:
            fsb = None

        sc = _gray_sc(len(pos))
        n = dlc_len(dlc, classic)
        w, poly = (21, 0x102899) if n > 16 else (17, 0x1685B)
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
        brs_raw = BRS_RAW_INDEX_EXT if extended else BRS_RAW_INDEX
        shift = sum(1 for (ri, _si, _sb) in pos if ri < brs_raw)

        seq_off = [k for k in range(len(field)) if k not in set(fsb_off)]
        base = len(st)

        return {
            "bits": bits,
            "brs_index": brs_raw + shift,
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
            "payload_bytes": n,
            "extended": extended,
            "classic": False,
            "header_len": HEADER_LEN_EXT if extended else HEADER_LEN,
        }


def frame_layout(fid, dlc, data, brs=True, extended=False, classic=False):
    """Full frame decomposition. Mirrors generate_can_fd_frame_ex exactly."""
    return _build(fid, dlc, data, brs, extended, classic)


def generate_can_fd_frame_ex(fid, dlc, data, brs=True, extended=False, classic=False):
    """Returns (bits, brs_index_in_stuffed_stream). brs_index=None for Classic CAN."""
    lay = _build(fid, dlc, data, brs, extended, classic)
    return lay["bits"], lay["brs_index"]


def generate_can_fd_frame(fid, dlc, data, brs=True, extended=False, classic=False):
    """Complete stuffed CAN/CAN FD frame, transmitter view (ACK recessive)."""
    return _build(fid, dlc, data, brs, extended, classic)["bits"]
