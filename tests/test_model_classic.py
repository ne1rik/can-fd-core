"""Classic CAN 2.0A/B conformance."""

import random
import pytest

from can_fd_reference import (
    dlc_len, generate_can_fd_frame, generate_can_fd_frame_ex, frame_layout,
    HEADER_LEN_CLASSIC, HEADER_LEN_CLASSIC_EXT,
)


def decode_back_classic(bits, lay):
    """Decode Classic CAN frame."""
    stuff = set(lay["dyn_stuff_indices"])
    raw = [b for i, b in enumerate(bits[:lay["stuffed_data_len"]]) if i not in stuff]
    
    if lay["extended"]:
        ida = 0
        for b in raw[1:12]:
            ida = (ida << 1) | b
        assert raw[12] == 1 and raw[13] == 1, "SRR/IDE must be recessive in Classic Extended"
        idb = 0
        for b in raw[14:32]:
            idb = (idb << 1) | b
        fid = (ida << 18) | idb
        ctrl = raw[32:39]  # RTR, r1, r0, DLC[3:0]
        dlc_bits = raw[35:39]
        data_start = 39
    else:
        fid = 0
        for b in raw[1:12]:
            fid = (fid << 1) | b
        ctrl = raw[12:19]  # RTR, IDE, r0, DLC[3:0]
        dlc_bits = raw[15:19]
        data_start = 19
    
    dlc = 0
    for b in dlc_bits:
        dlc = (dlc << 1) | b
    n = dlc_len(dlc, classic=True)
    data = []
    for k in range(n):
        v = 0
        for b in raw[data_start + 8*k : data_start + 8*k + 8]:
            v = (v << 1) | b
        data.append(v)
    return fid, dlc, data, ctrl


@pytest.mark.parametrize("fid", [0x000, 0x123, 0x7FF])
@pytest.mark.parametrize("dlc", range(9))  # Classic CAN: 0-8
@pytest.mark.parametrize("brs", [False])  # BRS ignored for Classic
def test_classic_base_roundtrip(fid, dlc, brs):
    n = dlc_len(dlc, classic=True)
    data = [(i * 37 + 11) & 0xFF for i in range(n)]
    bits = generate_can_fd_frame(fid, dlc, data, brs, extended=False, classic=True)
    lay = frame_layout(fid, dlc, data, brs, extended=False, classic=True)

    assert lay["bits"] == bits
    assert lay["header_len"] == HEADER_LEN_CLASSIC
    assert lay["raw_len"] == HEADER_LEN_CLASSIC + 8 * n
    assert len(bits) == lay["stuffed_data_len"] + 15 + 10  # CRC-15 + tail
    assert bits[-10:] == [1] * 10
    assert lay["brs_index"] is None  # No BRS in Classic
    assert lay["crc_width"] == 15
    assert lay["crc_field_len"] == 15
    assert lay["stuff_count_bits"] == []  # No SBC in Classic
    assert lay["fsb_indices"] == []  # No FSB in Classic

    got_id, got_dlc, got_data, ctrl = decode_back_classic(bits, lay)
    assert got_id == fid
    assert got_dlc == dlc
    assert got_data == data
    # RTR=0, IDE=0, r0=0
    assert ctrl[0] == 0 and ctrl[1] == 0 and ctrl[2] == 0


@pytest.mark.parametrize("fid", [0x00000000, 0x1FFFFFFF, 0x1127B78])
@pytest.mark.parametrize("dlc", range(9))
def test_classic_extended_roundtrip(fid, dlc, brs=False):
    n = dlc_len(dlc, classic=True)
    data = [(i * 37 + 11) & 0xFF for i in range(n)]
    bits = generate_can_fd_frame(fid, dlc, data, brs, extended=True, classic=True)
    lay = frame_layout(fid, dlc, data, brs, extended=True, classic=True)

    assert lay["bits"] == bits
    assert lay["header_len"] == HEADER_LEN_CLASSIC_EXT
    assert lay["raw_len"] == HEADER_LEN_CLASSIC_EXT + 8 * n
    assert len(bits) == lay["stuffed_data_len"] + 15 + 10
    assert bits[-10:] == [1] * 10
    assert lay["brs_index"] is None
    assert lay["crc_width"] == 15

    got_id, got_dlc, got_data, ctrl = decode_back_classic(bits, lay)
    assert got_id == fid
    assert got_dlc == dlc
    assert got_data == data
    # RTR=0, r1=0, r0=0
    assert ctrl[0] == 0 and ctrl[1] == 0 and ctrl[2] == 0


@pytest.mark.parametrize("dlc", range(9))
def test_classic_geometry(dlc):
    n = dlc_len(dlc, classic=True)
    lay = frame_layout(0x123, dlc, [0xA5] * n, False, extended=False, classic=True)
    assert lay["crc_field_len"] == 15
    assert len(lay["crc_bit_indices"]) == 15
    assert lay["fsb_indices"] == []
    st = lay["bits"][:lay["stuffed_data_len"]]
    run = 1
    for a, b in zip(st, st[1:]):
        run = run + 1 if a == b else 1
        assert run <= 5


def test_classic_differs_from_fd():
    """Same ID/DLC/data must produce different frames for Classic vs FD."""
    classic = generate_can_fd_frame(0x123, 8, [0xAA] * 8, False, extended=False, classic=True)
    fd = generate_can_fd_frame(0x123, 8, [0xAA] * 8, False, extended=False, classic=False)
    assert classic != fd
    assert len(classic) < len(fd)  # Classic has no BRS/ESI/res, smaller CRC


def test_classic_dlc_clamped():
    """Classic CAN DLC > 8 is clamped to 8 bytes."""
    for dlc in [9, 10, 15]:
        lay = frame_layout(0x123, dlc, [0xFF] * 64, False, classic=True)
        assert lay["payload_bytes"] == 8


def test_classic_randomised():
    rng = random.Random(20261114)
    for _ in range(100):
        dlc = rng.randrange(9)
        n = dlc_len(dlc, classic=True)
        data = [rng.randrange(256) for _ in range(n)]
        fid = rng.randrange(0x800) if rng.random() < 0.5 else rng.randrange(1 << 29)
        extended = fid >= 0x800
        bits = generate_can_fd_frame(fid, dlc, data, False, extended, classic=True)
        lay = frame_layout(fid, dlc, data, False, extended, classic=True)
        assert lay["bits"] == bits
