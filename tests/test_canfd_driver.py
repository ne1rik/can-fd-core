"""Unit tests for BRS-aware bit timing (no simulator required)."""

import pytest

from canfd_kit.bus.canfd_bus import CANFDDriver
from can_fd_reference import generate_can_fd_frame_ex


class _Sig:
    def __init__(self):
        self.value = 1


class _Dut:
    def __init__(self):
        self.rx = _Sig()
        self.tx = _Sig()


async def _capture_times(frame, brs_index, brs_enabled, arb, data):
    drv = CANFDDriver(_Dut(), "tx", "rx")
    times = []

    async def fake_send_bit(bit, bit_time_ns):
        times.append(bit_time_ns)

    drv.send_bit = fake_send_bit
    await drv.send_frame(frame, brs_index, brs_enabled,
                         arb_time_ns=arb, data_time_ns=data)
    return times


@pytest.mark.asyncio
async def test_brs_switches_after_brs_bit():
    arb, data = 2000.0, 500.0
    frame, bi = generate_can_fd_frame_ex(0x123, 9, [0xAA] * 12, True)
    times = await _capture_times(frame, bi, True, arb, data)

    assert len(times) == len(frame)
    assert all(t == arb for t in times[:bi + 1]), "bits up to BRS must use arb rate"
    assert all(t == data for t in times[bi + 1:]), "bits after BRS must use data rate"


@pytest.mark.asyncio
async def test_no_brs_keeps_arbitration_rate():
    arb, data = 2000.0, 500.0
    frame, bi = generate_can_fd_frame_ex(0x123, 9, [0xAA] * 12, False)
    times = await _capture_times(frame, bi, False, arb, data)

    assert len(times) == len(frame)
    assert all(t == arb for t in times), "BRS=0 must keep the whole frame at arb rate"
