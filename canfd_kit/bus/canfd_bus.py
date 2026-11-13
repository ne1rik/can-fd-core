"""CAN FD virtual bus: Driver and Monitor for cocotb 2.x."""

from cocotb.triggers import Timer, RisingEdge


class CANFDDriver:
    """Drives a pre-stuffed bitstream with BRS-aware bit timing."""

    def __init__(self, dut, tx_signal: str, rx_signal: str):
        self.dut = dut
        self.tx = getattr(dut, tx_signal)
        self.rx = getattr(dut, rx_signal)

    async def send_bit(self, bit: int, bit_time_ns: float):
        self.rx.value = bit
        await Timer(bit_time_ns, unit="ns")

    async def send_frame(self, bitstream, brs_index: int, brs_enabled: bool,
                         arb_time_ns: float = 2000.0,
                         data_time_ns: float = 500.0):
        """Bit rate switches starting with the bit AFTER BRS."""
        for i, bit in enumerate(bitstream):
            if brs_enabled and i > brs_index:
                await self.send_bit(bit, data_time_ns)
            else:
                await self.send_bit(bit, arb_time_ns)


class CANFDMonitor:
    """Captures a bit stream from a DUT's bit/valid pair.

    Must be started BEFORE the DUT is triggered. It waits for the first
    valid bit without counting idle cycles, so no leading bit is lost,
    then stops after `idle_cycles` consecutive invalid cycles.
    """

    def __init__(self, dut, bit_signal: str, valid_signal: str,
                 clk_signal: str = "clk"):
        self.dut = dut
        self.bit = getattr(dut, bit_signal)
        self.valid = getattr(dut, valid_signal)
        self.clk = getattr(dut, clk_signal)
        self.captured_bits = []

    async def capture_frame(self, timeout_cycles: int = 20000,
                            idle_cycles: int = 10):
        bits = []
        started = False
        low = 0
        for _ in range(timeout_cycles):
            await RisingEdge(self.clk)
            await Timer(1, unit="ns")      # let non-blocking assignments settle
            if int(self.valid.value) == 1:
                bits.append(int(self.bit.value))
                started = True
                low = 0
            elif started:
                low += 1
                if low >= idle_cycles:
                    break
        self.captured_bits = bits
        return bits
