"""FEFF (29-bit ID) conformance, plus FBFF non-regression anchors."""

import random
import pytest

from can_fd_reference import (
    dlc_len, generate_can_fd_frame, generate_can_fd_frame_ex, frame_layout,
    BRS_RAW_INDEX, BRS_RAW_INDEX_EXT, HEADER_LEN_EXT,
)


def decode_back(bits, lay):
    stuff = set(lay["dyn_stuff_indices"])
    raw = [b for i, b in enumerate(bits[:lay["stuffed_data_len"]]) if i not in stuff]
    if lay["extended"]:
        ida = 0
        for b in raw[1:12]:
            ida = (ida << 1) | b
        assert raw[12] == 1 and raw[13] == 1, "SRR/IDE must be recessive in FEFF"
        idb = 0
        for b in raw[14:32]:
            idb = (idb << 1) | b
        fid = (ida << 18) | idb
        ctrl = raw[32:41]
        dlc_bits = raw[37:41]
        data_start = 41
    else:
        fid = 0
        for b in raw[1:12]:
            fid = (fid << 1) | b
        ctrl = raw[12:22]
        dlc_bits = raw[18:22]
        data_start = 22
    dlc = 0
    for b in dlc_bits:
        dlc = (dlc << 1) | b
    n = dlc_len(dlc)
    data = []
    for k in range(n):
        v = 0
        for b in raw[data_start + 8*k : data_start + 8*k + 8]:
            v = (v << 1) | b
        data.append(v)
    return fid, dlc, data, ctrl


@pytest.mark.parametrize("fid", [0x00000000, 0x00000001, 0x1FFFFFFF,
                                 0x1127B78, 0x15555555, 0x0AAAAAAA, 0x00040000])
@pytest.mark.parametrize("dlc", [0, 1, 8, 10, 11, 15])
@pytest.mark.parametrize("brs", [False, True])
def test_feff_roundtrip(fid, dlc, brs):
    n = dlc_len(dlc)
    data = [(i * 37 + 11) & 0xFF for i in range(n)]
    bits = generate_can_fd_frame(fid, dlc, data, brs, extended=True)
    lay = frame_layout(fid, dlc, data, brs, extended=True)

    assert lay["bits"] == bits
    assert lay["header_len"] == HEADER_LEN_EXT
    assert lay["raw_len"] == HEADER_LEN_EXT + 8 * n
    assert len(bits) == lay["stuffed_data_len"] + lay["crc_field_len"] + 10
    assert bits[-10:] == [1] * 10
    assert bits[lay["brs_index"]] == int(brs)
    assert lay["crc_width"] == (21 if n > 16 else 17)

    got_id, got_dlc, got_data, ctrl = decode_back(bits, lay)
    assert got_id == fid, f"ID {got_id:#x} != {fid:#x}"
    assert got_dlc == dlc
    assert got_data == data
    # RRS=0, FDF=1, res=0, BRS, ESI=0
    assert ctrl[0] == 0 and ctrl[1] == 1 and ctrl[2] == 0
    assert ctrl[3] == int(brs) and ctrl[4] == 0


@pytest.mark.parametrize("dlc", range(16))
def test_feff_geometry(dlc):
    n = dlc_len(dlc)
    lay = frame_layout(0x12345678, dlc, [0xA5] * n, True, extended=True)
    w = 21 if n > 16 else 17
    seq = 4 + w
    assert lay["crc_field_len"] == 1 + seq + (seq - 1) // 4
    assert len(lay["crc_bit_indices"]) == w
    assert len(lay["sc_indices"]) == 4
    assert not (set(lay["fsb_indices"]) & set(lay["crc_bit_indices"]))
    st = lay["bits"][:lay["stuffed_data_len"]]
    run = 1
    for a, b in zip(st, st[1:]):
        run = run + 1 if a == b else 1
        assert run <= 5


def test_feff_brs_index_tracks_stuffing():
    for fid in (0x00000000, 0x1FFFFFFF, 0x15555555, 0x1127B78):
        bits, bi = generate_can_fd_frame_ex(fid, 8, [0xFF] * 8, True, extended=True)
        lay = frame_layout(fid, 8, [0xFF] * 8, True, extended=True)
        assert bi == lay["brs_index"]
        assert bits[bi] == 1
        bits0, bi0 = generate_can_fd_frame_ex(fid, 8, [0xFF] * 8, False, extended=True)
        assert bits0[bi0] == 0


def test_feff_differs_from_fbff():
    """Same low 11 bits must NOT produce the same frame in the two formats."""
    a = generate_can_fd_frame(0x123, 8, [0xAA] * 8, True, extended=False)
    b = generate_can_fd_frame(0x123, 8, [0xAA] * 8, True, extended=True)
    assert a != b
    assert len(b) > len(a)


def test_fbff_anchors_unchanged():
    """These are the CTU-verified anchors; they must not move."""
    for fid, dlc, pat, total in [(0x5AA, 8, 0xFF, 135), (0x123, 9, 0xAA, 155),
                                 (0x123, 9, 0x00, 174), (0x7FF, 15, 0xFF, 681),
                                 (0x000, 15, 0x00, 680)]:
        bits = generate_can_fd_frame(fid, dlc, [pat] * dlc_len(dlc), True)
        assert len(bits) == total


def test_feff_randomised_layout_agreement():
    rng = random.Random(20261114)
    for _ in range(200):
        dlc = rng.randrange(16)
        n = dlc_len(dlc)
        data = [rng.randrange(256) for _ in range(n)]
        fid = rng.randrange(1 << 29)
        brs = bool(rng.randrange(2))
        assert frame_layout(fid, dlc, data, brs, extended=True)["bits"] == \
            generate_can_fd_frame(fid, dlc, data, brs, extended=True)
