"""Adapter wiring the VIP to can_fd_loopback (the existing DUT)."""

import os

from canfd_vip import DUTAdapter, CanFrame
from can_fd_reference import dlc_len
import cocotb
from cocotb.triggers import RisingEdge

EXT = int(os.environ.get("EXTENDED", "0")) == 1
CLS = int(os.environ.get("CLASSIC", "0")) == 1


class LoopbackAdapter(DUTAdapter):
    """Адаптер для нашего can_fd_loopback."""

    def get_pins(self):
        return (self.dut.tx_bit, self.dut.rx_ack, self.dut.clk)

    def get_monitor_pins(self):
        """Шина наблюдения для BFM-монитора: (bus, valid strobe, clk)."""
        return (self.dut.tx_bit, self.dut.tx_bit_valid, self.dut.clk)

    async def init(self):
        self.dut.rst_n.value = 0
        self.dut.tx_start.value = 0
        self.dut.tx_data.value = 0
        await RisingEdge(self.dut.clk)
        await RisingEdge(self.dut.clk)
        self.dut.rst_n.value = 1
        await RisingEdge(self.dut.clk)

    async def request_tx(self, frame: CanFrame):
        n = dlc_len(frame.dlc, classic=frame.is_classic)
        self.dut.tx_id.value = frame.id
        self.dut.tx_dlc.value = frame.dlc
        self.dut.tx_brs.value = int(frame.brs)
        self.dut.tx_data.value = (
            int.from_bytes(bytes(frame.data), "big") << (512 - 8 * n)
        ) if n else 0

        self.dut.tx_start.value = 1
        await RisingEdge(self.dut.clk)
        await RisingEdge(self.dut.clk)
        self.dut.tx_start.value = 0

    async def read_rx(self) -> CanFrame:
        # Ждём rx_done, читаем rx_id/rx_dlc/rx_data
        for _ in range(100000):
            await RisingEdge(self.dut.clk)
            if int(self.dut.rx_done.value) == 1:
                n = dlc_len(int(self.dut.rx_dlc.value), classic=CLS)
                rx_data_int = int(self.dut.rx_data.value)
                data = []
                for k in range(n):
                    data.append((rx_data_int >> (512 - 8 * (k + 1))) & 0xFF)

                return CanFrame(
                    id=int(self.dut.rx_id.value),
                    dlc=int(self.dut.rx_dlc.value),
                    data=data,
                    brs=False,  # TODO: read brs_seen from DUT (not exported)
                    is_extended=EXT,   # build parameter of this loopback
                    is_classic=CLS     # build parameter of this loopback
                )
        return None
