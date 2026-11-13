"""Tests for CAN FD Virtual Bus arbitration logic."""
import pytest
import asyncio
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from canfd_kit.bus.virtual_bus import CANFDBus, CANFDBusDriver
from can_fd_reference import generate_can_fd_frame, dlc_len


@pytest.mark.asyncio
async def test_arbitration_lower_id_wins():
    """
    Node A (ID=0x100) and Node B (ID=0x200) start simultaneously.
    Node A must win arbitration because its ID is lower.
    """
    bus = CANFDBus()
    
    drv_a = CANFDBusDriver(bus, node_id=0xA)
    drv_b = CANFDBusDriver(bus, node_id=0xB)
    
    # Generate real CAN FD frames (DLC=8, 8 bytes of 0xAA, BRS=1)
    # Frame A: ID=0x100 -> bits: SOF(0) + 001 0000 0000 + ...
    # Frame B: ID=0x200 -> bits: SOF(0) + 010 0000 0000 + ...
    frame_a = generate_can_fd_frame(0x100, 8, [0xAA] * 8, brs=True)
    frame_b = generate_can_fd_frame(0x200, 8, [0xAA] * 8, brs=True)
    
    # Start both transmissions concurrently using standard asyncio
    task_a = asyncio.create_task(drv_a.send_frame(frame_a, bit_time_ns=10.0))
    task_b = asyncio.create_task(drv_b.send_frame(frame_b, bit_time_ns=10.0))
    
    # Wait for both to finish
    res_a = await task_a
    res_b = await task_b
    
    # Assertions
    assert res_a is True, "Node A (lower ID) should win arbitration and complete the frame"
    assert res_b is False, "Node B (higher ID) should lose arbitration"
    
    assert drv_a.arbitration_lost is False
    assert drv_b.arbitration_lost is True
    
    # Let's verify exactly WHERE Node B lost arbitration.
    # Bit 0: SOF (both send 0) -> bus=0, both win.
    # Bit 1: ID[10] (A sends 0, B sends 0) -> bus=0, both win.
    # Bit 2: ID[9]  (A sends 0, B sends 1) -> bus=0. A wins, B LOSES HERE.
    assert drv_b.lost_at_bit_index == 2, f"Node B should lose at bit index 2, but lost at {drv_b.lost_at_bit_index}"


@pytest.mark.asyncio
async def test_no_contention_single_node():
    """A single node on the bus should always succeed."""
    bus = CANFDBus()
    drv = CANFDBusDriver(bus, node_id=0x1)
    
    frame = generate_can_fd_frame(0x7FF, 15, [0xFF] * 64, brs=True)
    res = await drv.send_frame(frame, bit_time_ns=10.0)
    
    assert res is True
    assert drv.arbitration_lost is False
