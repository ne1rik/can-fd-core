"""CAN FD Virtual Bus Model.

Provides Driver and Monitor classes for cocotb, mimicking UVM agent behavior
but using native Python/cocotb primitives for Verilator compatibility.
"""
import cocotb
from cocotb.triggers import RisingEdge, FallingEdge, Timer
from cocotb.handle import LogicObject

class CANFDDriver:
    """Drives bits onto the virtual CAN FD bus."""
    def __init__(self, dut, tx_signal: str, rx_signal: str):
        self.dut = dut
        self.tx = getattr(dut, tx_signal)
        self.rx = getattr(dut, rx_signal)

    async def send_bit(self, bit: int, bit_time_ns: float = 10.0):
        """Drive a single bit and wait for the bit time."""
        self.rx.value = bit
        await Timer(bit_time_ns, units='ns')

    async def send_frame(self, bitstream: list[int], arb_time_ns: float = 2000.0, data_time_ns: float = 500.0):
        """Send a full pre-stuffed bitstream, handling BRS timing switch."""
        # M2.2: Implement BRS-aware timing switch here
        for bit in bitstream:
            await self.send_bit(bit, arb_time_ns)

class CANFDMonitor:
    """Sniffs the virtual CAN FD bus and reconstructs frames."""
    def __init__(self, dut, tx_signal: str, rx_signal: str):
        self.dut = dut
        self.tx = getattr(dut, tx_signal)
        self.rx = getattr(dut, rx_signal)
        self.received_frames = []

    async def sniff(self, timeout_ns: float = 10000.0):
        """Continuously monitor the bus for SOF (dominant 0)."""
        # M2.3: Implement edge detection and frame reconstruction here.
        # Note: @cocotb.coroutine was removed in cocotb 2.x. Use plain async def.
        pass
