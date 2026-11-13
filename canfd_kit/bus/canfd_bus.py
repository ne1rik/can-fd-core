"""CAN FD Virtual Bus Model."""
import cocotb
from cocotb.triggers import Timer

class CANFDDriver:
    """Drives bits onto the virtual CAN FD bus with BRS-aware timing."""
    
    def __init__(self, dut, tx_signal: str, rx_signal: str):
        self.dut = dut
        self.tx = getattr(dut, tx_signal)
        self.rx = getattr(dut, rx_signal)

    async def send_bit(self, bit: int, bit_time_ns: float):
        """Drive a single bit and wait for the bit time."""
        self.rx.value = bit
        await Timer(bit_time_ns, units='ns')

    async def send_frame(self, bitstream: list[int], brs_index: int, brs_enabled: bool, 
                         arb_time_ns: float = 2000.0, data_time_ns: float = 500.0):
        """
        Send a full pre-stuffed bitstream, handling BRS timing switch.
        
        Args:
            bitstream: List of bits (0/1), already stuffed.
            brs_index: Index of the BRS bit in the stuffed bitstream.
            brs_enabled: True if BRS bit is 1 (recessive), False otherwise.
            arb_time_ns: Bit time for arbitration phase (e.g., 2000.0 ns for 500 kbps).
            data_time_ns: Bit time for data phase (e.g., 500.0 ns for 2 Mbps).
        """
        if not bitstream:
            return

        for i, bit in enumerate(bitstream):
            # Скорость переключается начиная с бита, СЛЕДУЮЩЕГО за BRS
            if brs_enabled and i > brs_index:
                current_time_ns = data_time_ns
            else:
                current_time_ns = arb_time_ns
                
            await self.send_bit(bit, current_time_ns)


class CANFDMonitor:
    """Sniffs the virtual CAN FD bus and reconstructs frames."""
    def __init__(self, dut, tx_signal: str, rx_signal: str):
        self.dut = dut
        self.tx = getattr(dut, tx_signal)
        self.rx = getattr(dut, rx_signal)
        self.received_frames = []

    async def sniff(self, timeout_ns: float = 10000.0):
        """Continuously monitor the bus for SOF (dominant 0)."""
        pass
