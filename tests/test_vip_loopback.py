"""Loopback test через VIP-агенты (не использует dut.tx_id и т.д. напрямую).

Кадр проходит два независимых пути проверки:
  1. DUT RX: adapter.read_rx() (транзакция от приёмника DUT)
  2. Шина:   CanMonitor парсит биты с пина шины в CanFrame
             (с верификацией Stuff Count и CRC)
Оба сверяются со скорбордом против ожидаемого кадра.
"""
import os
import cocotb
from cocotb.clock import Clock
from canfd_vip import CanFrame, CanPinBFM, CanMonitor, CanScoreboard
from canfd_vip_loopback_adapter import LoopbackAdapter

EXT = int(os.environ.get("EXTENDED", "0")) == 1
CLS = int(os.environ.get("CLASSIC", "0")) == 1


@cocotb.test()
async def test_vip_loopback(dut):
    """Loopback через VIP: Driver -> BFM -> шина -> Monitor."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    # Инициализация
    adapter = LoopbackAdapter(dut)
    await adapter.init()

    bus_pin, strobe, clk = adapter.get_monitor_pins()
    bfm = CanPinBFM(None, bus_pin, clk, valid_strobe=strobe)
    monitor = CanMonitor(bfm)
    scoreboard = CanScoreboard()

    # Тестовый кадр (формат определяется конфигурацией сборки DUT)
    fid = 0x1127B78 if EXT else 0x123
    frame = CanFrame(
        id=fid, dlc=8,
        data=[0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88],
        brs=False, is_extended=EXT, is_classic=CLS
    )

    # Монитор шины стартует до передачи
    mon_task = cocotb.start_soon(monitor.recv(timeout_ns=100000))

    # Отправляем через DUT (не через BFM напрямую)
    await adapter.request_tx(frame)
    # Два независимых наблюдения одной передачи: приёмник DUT и монитор шины
    scoreboard.expect(frame)
    scoreboard.expect(frame)

    # Путь 1: кадр от приёмника DUT
    received = await adapter.read_rx()
    assert received is not None, "Frame not received by DUT"
    scoreboard.check(received)

    # Путь 2: кадр, распарсенный монитором из бит шины
    bus_frame = await mon_task
    assert bus_frame is not None, "Monitor did not parse a frame from the bus"
    scoreboard.check(bus_frame)

    # Сверка
    assert received == frame, f"DUT RX mismatch: {received} != {frame}"
    assert bus_frame == frame, f"Bus monitor mismatch: {bus_frame} != {frame}"

    rep = scoreboard.report()
    for kind, bad in scoreboard.mismatches:
        cocotb.log.info("scoreboard mismatch (%s): %s", kind, bad)
    cocotb.log.info("expected: %s", frame)
    cocotb.log.info("dut rx  : %s", received)
    cocotb.log.info("monitor : %s", bus_frame)
    assert rep["expected_remaining"] == 0, f"scoreboard: {rep}"
    assert rep["mismatches"] == 0, f"scoreboard: {rep}"
