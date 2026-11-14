"""CAN/CAN FD VIP: transaction-level decoupling from DUT specifics.

Layers:
  CanFrame      - pure transaction, knows nothing about any DUT
  CanPinBFM     - pin level: drive/sample bits (timed bus mode or
                  protocol-clock mode driven by a valid strobe)
  CanDriver     - sends CanFrames onto the bus through the BFM
  CanMonitor    - captures bus bits through the BFM and parses them into
                  CanFrames (with Stuff Count / CRC verification)
  CanScoreboard - expected vs received bookkeeping
  DUTAdapter    - contract every concrete DUT must implement
"""

from dataclasses import dataclass
from typing import List, Optional

import cocotb
from cocotb.triggers import RisingEdge, Timer

from can_fd_reference import generate_can_fd_frame, frame_layout, dlc_len, _crc_val


@dataclass
class CanFrame:
    """Транзакция CAN/CAN FD. Не знает о DUT."""
    id: int
    dlc: int
    data: List[int]
    brs: bool = False
    is_extended: bool = False
    is_classic: bool = False

    def __eq__(self, other):
        if not isinstance(other, CanFrame):
            return False
        return (self.id == other.id and self.dlc == other.dlc and
                self.data == other.data and self.brs == other.brs and
                self.is_extended == other.is_extended and
                self.is_classic == other.is_classic)

    def __repr__(self):
        fmt = ("FEFF" if self.is_extended else "FBFF") if not self.is_classic \
            else ("CExt" if self.is_extended else "CBase")
        return (f"CanFrame({fmt} id={self.id:#x} dlc={self.dlc} brs={int(self.brs)} "
                f"data={bytes(self.data).hex()})")


class CanFrameParser:
    """Bit-level ISO 11898-1 parser: fed with bus bits starting at SOF,
    returns a CanFrame once the frame is complete.

    Handles dynamic destuffing of header+payload, the CAN FD fixed-stuff
    CRC field (including the boundary case where the 5th same-valued bit
    is the last raw bit), Classic CRC within the dynamically stuffed
    region, Stuff Count verification (Gray + parity) and CRC verification
    against the golden model.
    """

    PHASE_DYN = "dyn"
    PHASE_FIELD = "field"
    PHASE_TAIL = "tail"

    def __init__(self):
        self.reset()

    def reset(self):
        self.raw = []            # destuffed raw bits (header+payload[+CRC for classic])
        self.st = []             # stuffed stream: FD CRC is computed over it
        self.stuff_count = 0     # dynamic stuff bits inserted (FD Stuff Count)
        self.run_bit = None
        self.run = 0
        self.expect_stuff = False
        self.ide = None
        self.fmt = None          # 'base' | 'ext'
        self.is_classic = None
        self.header_len = None
        self.raw_total = None
        self.crc_width = None
        self.dlc = None
        self.phase = self.PHASE_DYN
        self.seq = []            # SC + CRC bits collected from the FD field
        self.field_pos = 0
        self.field_len = None
        self.groups = None
        self.tail_cnt = 0

    def _decode_header(self):
        n = len(self.raw)
        if n == 14:
            self.ide = self.raw[13]
        if self.ide == 0 and n == 15:
            self.fmt = "base"
            self.is_classic = (self.raw[14] == 0)
            self.header_len = 19 if self.is_classic else 22
        elif self.ide == 1 and n == 34:
            self.fmt = "ext"
            self.is_classic = (self.raw[33] == 0)
            self.header_len = 39 if self.is_classic else 41
        if self.header_len is not None and n == self.header_len and self.dlc is None:
            self.dlc = 0
            for k in range(4):
                self.dlc = (self.dlc << 1) | self.raw[self.header_len - 4 + k]
            pay = dlc_len(self.dlc, classic=self.is_classic)
            if self.is_classic:
                self.raw_total = self.header_len + 8 * pay + 15
            else:
                self.raw_total = self.header_len + 8 * pay
                self.crc_width = 21 if pay > 16 else 17

    def _start_field(self):
        self.phase = self.PHASE_FIELD
        self.field_pos = 0
        seq_len = 4 + self.crc_width
        self.groups = -(-seq_len // 4)          # ceil
        self.field_len = seq_len + self.groups  # leading FSB + groups with FSBs between

    def _finish_field(self):
        sc = self.seq[:4]
        crcb = self.seq[4:]
        n = self.stuff_count % 8
        g = n ^ (n >> 1)
        exp_sc = [(g >> i) & 1 for i in (2, 1, 0)]
        exp_sc.append(sum(exp_sc) % 2)
        if sc != exp_sc:
            raise ValueError(f"Stuff Count mismatch: got {sc}, expected {exp_sc} "
                             f"(stuff_count={self.stuff_count})")
        w = self.crc_width
        poly = 0x102899 if w == 21 else 0x1685B
        v = _crc_val(self.st + sc, w, poly, 1 << (w - 1))
        exp_crc = [(v >> i) & 1 for i in range(w - 1, -1, -1)]
        if crcb != exp_crc:
            raise ValueError(f"CRC mismatch: got {crcb}, expected {exp_crc}")

    def _build_frame(self):
        h = self.header_len
        base_id = 0
        for b in self.raw[1:12]:
            base_id = (base_id << 1) | b
        if self.fmt == "ext":
            ext_id = 0
            for b in self.raw[14:32]:
                ext_id = (ext_id << 1) | b
            fid = (base_id << 18) | ext_id
        else:
            fid = base_id
        brs = False if self.is_classic else bool(self.raw[16 if self.fmt == "base" else 35])
        pay = dlc_len(self.dlc, classic=self.is_classic)
        data = []
        for k in range(pay):
            byte = 0
            for b in self.raw[h + 8 * k: h + 8 * k + 8]:
                byte = (byte << 1) | b
            data.append(byte)
        return CanFrame(id=fid, dlc=self.dlc, data=data, brs=brs,
                        is_extended=(self.fmt == "ext"), is_classic=self.is_classic)

    def feed(self, bit: int) -> Optional[CanFrame]:
        """Feed one bus bit; returns the CanFrame when the frame is done."""
        if self.phase == self.PHASE_DYN:
            if self.expect_stuff:
                # This bit is the dynamically inserted stuff bit.
                self.expect_stuff = False
                self.st.append(bit)
                self.stuff_count += 1
                self.run_bit = bit
                self.run = 1
                if self.is_classic and len(self.raw) == self.raw_total:
                    # Classic: stuffing covers raw+CRC; a stuff bit may land
                    # after the 15th CRC bit, before the CRC delimiter.
                    self.phase = self.PHASE_TAIL
                return None

            self.raw.append(bit)
            self.st.append(bit)
            if bit == self.run_bit:
                self.run += 1
            else:
                self.run_bit, self.run = bit, 1

            self._decode_header()

            if self.run == 5:
                if self.raw_total is None or len(self.raw) < self.raw_total:
                    self.expect_stuff = True
                elif self.is_classic:
                    # Classic stuffs even after the very last CRC bit.
                    self.expect_stuff = True
                else:
                    # CAN FD boundary: the would-be stuff bit is replaced by
                    # the fixed stuff bit that opens the CRC field.
                    self._start_field()
            elif self.raw_total is not None and len(self.raw) == self.raw_total:
                if self.is_classic:
                    self.phase = self.PHASE_TAIL
                else:
                    self._start_field()
            return None

        if self.phase == self.PHASE_FIELD:
            # FSBs sit at every 5th position: 0, 5, 10, ... (leading FSB +
            # one after each 4-bit group except the last).
            if self.field_pos % 5 != 0:
                self.seq.append(bit)
            self.field_pos += 1
            if self.field_pos == self.field_len:
                self._finish_field()
                self.phase = self.PHASE_TAIL
            return None

        if self.phase == self.PHASE_TAIL:
            self.tail_cnt += 1
            if self.tail_cnt == 10:
                return self._build_frame()
            return None

        return None


class CanPinBFM:
    """Bus Functional Model: физический уровень (drive/sample битов).

    Два режима:
      - timed (по умолчанию): биты драйвятся/сэмплируются по абсолютным
        длительностям nominal_bit_ns / data_bit_ns.
      - protocol-clock (valid_strobe задан): каждый бит сопровождается
        стробом DUT (например tx_bit_valid); drive/sample синхронны к такту.
    """

    def __init__(self, tx_pin, rx_pin, clk, nominal_bit_ns=2000, data_bit_ns=500,
                 valid_strobe=None, clk_period_ns=10):
        self.tx_pin = tx_pin
        self.rx_pin = rx_pin
        self.clk = clk
        self.nominal_bit_ns = nominal_bit_ns
        self.data_bit_ns = data_bit_ns
        self.valid_strobe = valid_strobe
        self.clk_period_ns = clk_period_ns
        if self.tx_pin is not None:
            self.tx_pin.value = 1  # recessive

    async def drive_bit(self, bit: int, duration_ns: int):
        """Драйвит один бит заданной длительности."""
        if self.valid_strobe is not None:
            while True:
                await RisingEdge(self.clk)
                await Timer(1, unit="ns")
                if int(self.valid_strobe.value) == 1:
                    break
            self.tx_pin.value = bit
        else:
            self.tx_pin.value = bit
            await Timer(duration_ns, unit="ns")

    async def sample_bit(self, sample_offset_ns: int = None,
                         timeout_ns: int = None) -> Optional[int]:
        """Сэмплирует один бит.

        timed-режим: ждёт sample_offset_ns (по умолчанию 75% номинального
        бита), читает шину, дожидается конца слота и возвращает значение.
        protocol-clock-режим: ждёт такт со стробом и читает шину.
        Возвращает None по таймауту (только стробный режим).
        """
        if self.valid_strobe is not None:
            max_cycles = (timeout_ns // self.clk_period_ns) if timeout_ns else None
            waited = 0
            while True:
                await RisingEdge(self.clk)
                await Timer(1, unit="ns")
                if int(self.valid_strobe.value) == 1:
                    return int(self.rx_pin.value)
                if max_cycles is not None:
                    waited += 1
                    if waited >= max_cycles:
                        return None
        if sample_offset_ns is None:
            sample_offset_ns = int(self.nominal_bit_ns * 0.75)
        await Timer(sample_offset_ns, unit="ns")
        bit = int(self.rx_pin.value)
        await Timer(self.nominal_bit_ns - sample_offset_ns, unit="ns")
        return bit


class CanDriver:
    """Отправляет CanFrame в шину через BFM.

    Не знает о DUT, только о BFM и эталонной модели.
    """

    def __init__(self, bfm: CanPinBFM):
        self.bfm = bfm

    async def send(self, frame: CanFrame):
        """Отправляет кадр. Использует эталонную модель для генерации битов."""
        bits = generate_can_fd_frame(
            frame.id, frame.dlc, frame.data, frame.brs,
            extended=frame.is_extended, classic=frame.is_classic
        )

        brs_index = None
        if not frame.is_classic:
            layout = frame_layout(frame.id, frame.dlc, frame.data, frame.brs,
                                  extended=frame.is_extended, classic=frame.is_classic)
            brs_index = layout["brs_index"]

        for i, bit in enumerate(bits):
            if frame.brs and brs_index is not None and i > brs_index:
                duration = self.bfm.data_bit_ns
            else:
                duration = self.bfm.nominal_bit_ns
            await self.bfm.drive_bit(bit, duration)


class CanMonitor:
    """Слушает шину и собирает CanFrame.

    Не знает о DUT, только о BFM и эталонной модели (для верификации CRC).
    """

    def __init__(self, bfm: CanPinBFM):
        self.bfm = bfm

    async def recv(self, timeout_ns: int = 1_000_000) -> Optional[CanFrame]:
        """Принимает один кадр: ждёт SOF (recessive -> dominant), парсит
        биты по ISO 11898-1. Возвращает None по таймауту."""
        parser = CanFrameParser()
        started = False
        prev = 1
        while True:
            bit = await self.bfm.sample_bit(
                timeout_ns=None if started else timeout_ns)
            if bit is None:
                return None
            if not started:
                if prev == 1 and bit == 0:
                    started = True
                    frame = parser.feed(bit)
                    if frame is not None:
                        return frame
                prev = bit
            else:
                frame = parser.feed(bit)
                if frame is not None:
                    return frame


class CanScoreboard:
    """Сравнивает ожидаемые и принятые кадры."""
    def __init__(self):
        self.expected = []
        self.received = []
        self.mismatches = []

    def expect(self, frame: CanFrame):
        self.expected.append(frame)

    def check(self, frame: CanFrame):
        self.received.append(frame)
        if frame not in self.expected:
            self.mismatches.append(("unexpected", frame))
        else:
            self.expected.remove(frame)

    def report(self):
        return {
            "expected_remaining": len(self.expected),
            "received": len(self.received),
            "mismatches": len(self.mismatches)
        }


class DUTAdapter:
    """Контракт адаптера DUT.

    Каждый конкретный DUT реализует свой адаптер, наследуя этот интерфейс.
    """
    def __init__(self, dut):
        self.dut = dut

    def get_pins(self):
        """Возвращает (tx_pin, rx_pin, clk) для BFM."""
        raise NotImplementedError

    async def init(self):
        """Инициализация DUT (reset, конфигурация регистров если нужно)."""
        raise NotImplementedError

    async def request_tx(self, frame: CanFrame):
        """Попросить DUT передать кадр (для тестов, где DUT = TX)."""
        raise NotImplementedError

    async def read_rx(self) -> Optional[CanFrame]:
        """Прочитать принятый кадр из DUT (для тестов, где DUT = RX)."""
        raise NotImplementedError
