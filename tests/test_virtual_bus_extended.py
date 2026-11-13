"""Wired-AND bus and arbitration: contention, exact loss index, identical frames."""

import asyncio
import pytest

from canfd_kit.bus.virtual_bus import CANFDBus, CANFDBusDriver
from can_fd_reference import generate_can_fd_frame


def test_idle_bus_is_recessive():
    bus = CANFDBus()
    bus.register(0)
    bus.register(1)
    assert bus._resolve() == 1


def test_dominant_wins():
    bus = CANFDBus()
    bus.register(0)
    bus.register(1)
    bus.drivers[0] = 1
    bus.drivers[1] = 0
    assert bus._resolve() == 0


@pytest.mark.parametrize("low,high,expect_index", [
    (0x100, 0x200, 2),    # divergence at ID[9], no stuffing before
    (0x000, 0x7FF, 1),    # divergence at ID[10], no stuffing before
    (0x001, 0x003, 12),   # divergence at ID[1], after two stuff bits
    (0x555, 0x7FF, 2),    # divergence at ID[9], no stuffing before
])
@pytest.mark.asyncio
async def test_lower_id_wins_at_expected_bit(low, high, expect_index):
    """
    Core CAN property: the lower ID wins arbitration at a specific bit.
    The expected index is in the STUFFED bitstream.
    """
    bus = CANFDBus()
    a = CANFDBusDriver(bus, node_id=0xA)
    b = CANFDBusDriver(bus, node_id=0xB)
    fa = generate_can_fd_frame(low, 8, [0xAA] * 8, True)
    fb = generate_can_fd_frame(high, 8, [0xAA] * 8, True)

    ta = asyncio.create_task(a.send_frame(fa, bit_time_ns=1.0))
    tb = asyncio.create_task(b.send_frame(fb, bit_time_ns=1.0))
    ra, rb = await ta, await tb

    assert ra is True and a.arbitration_lost is False, \
        f"lower ID {low:#05x} should win"
    assert rb is False and b.arbitration_lost is True, \
        f"higher ID {high:#05x} should lose"
    assert b.lost_at_bit_index == expect_index, \
        f"expected loss at stuffed index {expect_index}, got {b.lost_at_bit_index}"


@pytest.mark.asyncio
async def test_identical_ids_both_complete():
    """Same ID, same payload: no mismatch, both finish the frame."""
    bus = CANFDBus()
    a = CANFDBusDriver(bus, node_id=1)
    b = CANFDBusDriver(bus, node_id=2)
    f = generate_can_fd_frame(0x123, 8, [0xAA] * 8, True)
    ra, rb = await asyncio.gather(
        asyncio.create_task(a.send_frame(f, bit_time_ns=1.0)),
        asyncio.create_task(b.send_frame(f, bit_time_ns=1.0)),
    )
    assert ra is True and rb is True, "identical frames must both complete"
    assert a.arbitration_lost is False and b.arbitration_lost is False


@pytest.mark.asyncio
async def test_three_nodes_lowest_wins():
    bus = CANFDBus()
    drivers = [CANFDBusDriver(bus, node_id=i) for i in range(3)]
    frames = [generate_can_fd_frame(i, 8, [0x55] * 8, True)
              for i in (0x300, 0x100, 0x200)]
    tasks = [asyncio.create_task(d.send_frame(f, bit_time_ns=1.0))
             for d, f in zip(drivers, frames)]
    results = await asyncio.gather(*tasks)
    assert results == [False, True, False]
    assert [d.arbitration_lost for d in drivers] == [True, False, True]


@pytest.mark.asyncio
async def test_sequential_frames_no_contention():
    bus = CANFDBus()
    d = CANFDBusDriver(bus, node_id=1)
    for fid in (0x100, 0x200, 0x7FF):
        f = generate_can_fd_frame(fid, 8, [0xFF] * 8, True)
        assert await d.send_frame(f, bit_time_ns=1.0) is True
        assert d.arbitration_lost is False


@pytest.mark.asyncio
async def test_recessive_node_scheduled_first():
    """
    Previously xfail: recessive node created first could miss arbitration loss.
    With two-phase settle/sample, task creation order no longer matters.
    """
    bus = CANFDBus()
    a = CANFDBusDriver(bus, node_id=0xA)   # lower ID, dominant at diff bit
    b = CANFDBusDriver(bus, node_id=0xB)   # higher ID, recessive
    fa = generate_can_fd_frame(0x100, 8, [0xAA] * 8, True)
    fb = generate_can_fd_frame(0x200, 8, [0xAA] * 8, True)

    # Deliberately schedule the recessive node FIRST
    tb = asyncio.create_task(b.send_frame(fb, bit_time_ns=1.0))
    ta = asyncio.create_task(a.send_frame(fa, bit_time_ns=1.0))
    ra, rb = await ta, await tb

    assert ra is True and a.arbitration_lost is False
    assert rb is False and b.arbitration_lost is True, \
        "higher ID must lose regardless of task creation order"
