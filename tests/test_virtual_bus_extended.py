"""Wired-AND bus and arbitration: basic contention scenarios."""

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


@pytest.mark.asyncio
async def test_single_node_completes():
    """Single node on the bus should always succeed."""
    bus = CANFDBus()
    drv = CANFDBusDriver(bus, node_id=1)
    frame = generate_can_fd_frame(0x123, 8, [0xAA] * 8, True)
    result = await drv.send_frame(frame, bit_time_ns=1.0)
    assert result is True
    assert drv.arbitration_lost is False


@pytest.mark.asyncio
async def test_three_nodes_lowest_wins():
    """Three nodes: lowest ID should win."""
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
    """Sequential frames from single node should all succeed."""
    bus = CANFDBus()
    d = CANFDBusDriver(bus, node_id=1)
    for fid in (0x100, 0x200, 0x7FF):
        f = generate_can_fd_frame(fid, 8, [0xFF] * 8, True)
        assert await d.send_frame(f, bit_time_ns=1.0) is True
        assert d.arbitration_lost is False
