"""Reference model conformance: anchors, catalogue CRCs, layout agreement."""

import random
import pytest

from can_fd_reference import (
    dlc_len, stuff_bits, calculate_crc,
    generate_can_fd_frame, generate_can_fd_frame_ex, frame_layout,
)


# --- anchors locked against the RTL and the public CANalyzer vector ---------

@pytest.mark.parametrize("fid,dlc,pattern,total", [
    (0x5AA, 8, 0xFF, 135),
    (0x123, 9, 0xAA, 155),
    (0x123, 9, 0x00, 174),
    (0x7FF, 15, 0xFF, 681),
    (0x000, 15, 0x00, 680),
])
def test_frame_length_anchors(fid, dlc, pattern, total):
    bits = generate_can_fd_frame(fid, dlc, [pattern] * dlc_len(dlc), True)
    assert len(bits) == total


def test_anchor_crc17_value():
    """V-001: FBFF 0x5AA / DLC8 / 8xFF -> CRC-17 = 0x006BD."""
    lay = frame_layout(0x5AA, 8, [0xFF] * 8, True)
    assert lay["crc_width"] == 17
    assert lay["crc_value"] == 0x006BD


# --- catalogue CRC checks (init = 0, no reflection) ------------------------

def _ascii_bits(s):
    return [(b >> i) & 1 for b in s.encode() for i in range(7, -1, -1)]


def test_crc17_catalogue_check():
    """V-002: CRC-17/CAN-FD over '123456789' = 0x04F03."""
    bits = calculate_crc(_ascii_bits("123456789"), 8)
    val = int("".join(map(str, bits)), 2)
    assert val == 0x04F03


def test_crc21_catalogue_check():
    """V-003: CRC-21/CAN-FD over '123456789' = 0x0ED841."""
    bits = calculate_crc(_ascii_bits("123456789"), 64)
    val = int("".join(map(str, bits)), 2)
    assert val == 0x0ED841


# --- structural invariants -------------------------------------------------

def test_dlc_mapping():
    assert [dlc_len(d) for d in range(16)] == \
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 12, 16, 20, 24, 32, 48, 64]


def test_stuff_rule_inserts_after_five():
    out, pos = stuff_bits([0] * 5)
    assert out == [0, 0, 0, 0, 0, 1]
    assert len(pos) == 1


def test_stuff_bit_starts_next_run():
    # Ten zeros -> stuff 1 after 5, then the run restarts from that 1,
    # so the next five zeros trigger another stuff bit.
    out, pos = stuff_bits([0] * 10)
    assert out == [0]*5 + [1] + [0]*5 + [1]
    assert len(pos) == 2


def test_no_six_identical_in_stuffed_region():
    for fid in (0x000, 0x7FF, 0x555, 0x123):
        for pattern in (0x00, 0xFF, 0xAA, 0x55):
            lay = frame_layout(fid, 15, [pattern] * 64, True)
            st = lay["bits"][:lay["stuffed_data_len"]]
            run = 1
            for a, b in zip(st, st[1:]):
                run = run + 1 if a == b else 1
                assert run <= 5, f"six-bit run in stuffed region: fid={fid:#x}"


@pytest.mark.parametrize("dlc", range(16))
@pytest.mark.parametrize("brs", [False, True])
def test_layout_matches_generator(dlc, brs):
    n = dlc_len(dlc)
    data = [(i * 37 + 11) & 0xFF for i in range(n)]
    for fid in (0x000, 0x123, 0x7FF):
        bits = generate_can_fd_frame(fid, dlc, data, brs)
        lay = frame_layout(fid, dlc, data, brs)
        assert lay["bits"] == bits, "layout drifted from generator"


@pytest.mark.parametrize("dlc", range(16))
def test_layout_geometry(dlc):
    n = dlc_len(dlc)
    lay = frame_layout(0x123, dlc, [0xA5] * n, True)
    w = 21 if n > 16 else 17
    seq = 4 + w
    assert lay["crc_width"] == w
    assert lay["crc_field_len"] == 1 + seq + (seq - 1) // 4
    assert lay["tail_len"] == 10
    assert len(lay["bits"]) == lay["stuffed_data_len"] + lay["crc_field_len"] + 10
    assert lay["tail_start"] + 10 == len(lay["bits"])
    assert lay["bits"][-10:] == [1] * 10          # delim, ACK, delim, EOF x7
    assert len(lay["crc_bit_indices"]) == w
    assert len(lay["sc_indices"]) == 4
    # fixed stuff bits must not be inside the CRC input index sets
    assert not (set(lay["fsb_indices"]) & set(lay["crc_bit_indices"]))
    assert not (set(lay["fsb_indices"]) & set(lay["sc_indices"]))


def test_brs_index_tracks_stuffing():
    for fid in (0x000, 0x123, 0x5AA, 0x7FF):
        bits, bi = generate_can_fd_frame_ex(fid, 8, [0xFF] * 8, True)
        lay = frame_layout(fid, 8, [0xFF] * 8, True)
        assert bi == lay["brs_index"]
        assert bits[bi] == 1                     # BRS recessive when enabled
        bits0, bi0 = generate_can_fd_frame_ex(fid, 8, [0xFF] * 8, False)
        assert bits0[bi0] == 0


def test_randomised_layout_agreement():
    rng = random.Random(20261113)
    for _ in range(300):
        dlc = rng.randrange(16)
        n = dlc_len(dlc)
        data = [rng.randrange(256) for _ in range(n)]
        fid = rng.randrange(0x800)
        brs = bool(rng.randrange(2))
        assert frame_layout(fid, dlc, data, brs)["bits"] == \
            generate_can_fd_frame(fid, dlc, data, brs)
