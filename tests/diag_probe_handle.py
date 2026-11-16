"""Diagnostic: how is the 512-bit tx_data port exposed, and when."""

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge


def _try(dut, label, fn):
    try:
        fn()
        cocotb.log.info("PROBE %s -> OK", label)
        return True
    except Exception as exc:
        cocotb.log.info("PROBE %s -> %s: %s", label, type(exc).__name__, exc)
        return False


@cocotb.test()
async def probe(dut):
    cocotb.log.info("PROBE handle type=%s len=%s",
                    type(dut.tx_data).__name__, len(dut.tx_data))

    # at time 0, before any clock edge
    _try(dut, "t0 int", lambda: setattr(dut.tx_data, "value", 0))
    _try(dut, "t0 str512", lambda: setattr(dut.tx_data, "value", "0" * 512))

    def _la():
        from cocotb.types import LogicArray
        dut.tx_data.value = LogicArray("0" * 512)
    _try(dut, "t0 LogicArray", _la)

    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    dut.rst_n.value = 0
    dut.tx_start.value = 0
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)

    # after the clock is running
    cocotb.log.info("PROBE handle type after clk=%s", type(dut.tx_data).__name__)
    _try(dut, "clk int", lambda: setattr(dut.tx_data, "value", 0))
    _try(dut, "clk str512", lambda: setattr(dut.tx_data, "value", "0" * 512))
    _try(dut, "clk LogicArray", _la)
