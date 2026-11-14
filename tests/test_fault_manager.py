"""Fault confinement tests: TEC/REC, state transitions, error frame, bus-off recovery."""
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer


async def setup(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    dut.rst_n.value = 0
    dut.tx_error.value = 0
    dut.tx_done.value = 0
    dut.tx_active.value = 0
    dut.rx_error.value = 0
    dut.rx_valid.value = 0
    dut.bus_idle.value = 1
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)


@cocotb.test()
async def test_error_active_to_passive(dut):
    """TEC >= 128 transitions node to ERROR_PASSIVE."""
    await setup(dut)

    # Initial state: ERROR_ACTIVE, TEC=0
    assert int(dut.state.value) == 0, "Initial state must be ERROR_ACTIVE"
    assert int(dut.tec.value) == 0

    # Generate 16 TX errors (16 * 8 = 128)
    for i in range(16):
        dut.tx_error.value = 1
        await RisingEdge(dut.clk)
        dut.tx_error.value = 0
        await RisingEdge(dut.clk)
        await RisingEdge(dut.clk)  # allow counter update

    # TEC should be 128, state ERROR_PASSIVE
    assert int(dut.tec.value) == 128, f"TEC should be 128, got {int(dut.tec.value)}"
    assert int(dut.state.value) == 1, "State should be ERROR_PASSIVE"


@cocotb.test()
async def test_bus_off_at_256(dut):
    """TEC >= 256 transitions node to BUS_OFF."""
    await setup(dut)
    assert int(dut.state.value) == 0

    # 32 TX errors * 8 = 256 -> BUS_OFF
    for i in range(32):
        dut.tx_error.value = 1
        await RisingEdge(dut.clk)
        dut.tx_error.value = 0
        await RisingEdge(dut.clk)
        await RisingEdge(dut.clk)

    assert int(dut.state.value) == 2, "State should be BUS_OFF"
    assert int(dut.bus_off.value) == 1, "bus_off output must be asserted"
    assert int(dut.tec.value) == 255, f"TEC reads 255 while bus-off, got {int(dut.tec.value)}"

    # A bus-off node is disconnected: no error flags may be generated.
    dut.tx_error.value = 1
    await Timer(1, unit="ns")
    assert int(dut.error_flag_active.value) == 0, "active error flag must be off in bus-off"
    assert int(dut.error_flag_passive.value) == 0, "passive error flag must be off in bus-off"
    dut.tx_error.value = 0
    await RisingEdge(dut.clk)


@cocotb.test()
async def test_bus_off_recovery(dut):
    """128 x 11 recessive bits recovers from BUS OFF."""
    await setup(dut)

    # Enter bus-off: 32 TX errors * 8 = 256
    for i in range(32):
        dut.tx_error.value = 1
        await RisingEdge(dut.clk)
        dut.tx_error.value = 0
        await RisingEdge(dut.clk)
        await RisingEdge(dut.clk)
    assert int(dut.state.value) == 2, "State should be BUS_OFF before recovery"

    # Partial recovery progress...
    dut.bus_idle.value = 1
    for _ in range(500):
        await RisingEdge(dut.clk)
    # ...interrupted by bus activity: recovery counter must restart.
    dut.bus_idle.value = 0
    for _ in range(20):
        await RisingEdge(dut.clk)
    dut.bus_idle.value = 1

    # 128 x 11 = 1408 recessive bits -> full recovery sequence
    saw_recovered = False
    for _ in range(1450):
        await RisingEdge(dut.clk)
        await Timer(1, unit="ns")
        if int(dut.recovered.value) == 1:
            saw_recovered = True

    assert saw_recovered, "recovered pulse not observed after 1408 idle cycles"
    assert int(dut.state.value) == 0, "State should be ERROR_ACTIVE after recovery"
    assert int(dut.tec.value) == 0, f"TEC should be 0 after recovery, got {int(dut.tec.value)}"
    assert int(dut.rec.value) == 0, f"REC should be 0 after recovery, got {int(dut.rec.value)}"
    assert int(dut.bus_off.value) == 0, "bus_off must be deasserted after recovery"


@cocotb.test()
async def test_rx_error_increments_rec(dut):
    """RX error increments REC."""
    await setup(dut)

    # 130 RX errors: REC counts 1..130; at >=128 the node goes passive
    for i in range(130):
        dut.rx_error.value = 1
        await RisingEdge(dut.clk)
        dut.rx_error.value = 0
        await RisingEdge(dut.clk)
        await RisingEdge(dut.clk)

    assert int(dut.rec.value) == 130, f"REC should be 130, got {int(dut.rec.value)}"
    assert int(dut.state.value) == 1, "REC >= 128 must put node into ERROR_PASSIVE"

    # Successful receptions decrement REC back to 0 and restore ERROR_ACTIVE
    dut.rx_valid.value = 1
    for _ in range(130):
        await RisingEdge(dut.clk)
    dut.rx_valid.value = 0
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)

    assert int(dut.rec.value) == 0, f"REC should be 0, got {int(dut.rec.value)}"
    assert int(dut.state.value) == 0, "Node should return to ERROR_ACTIVE"


@cocotb.test()
async def test_successful_tx_decrements_tec(dut):
    """Successful TX decrements TEC by 1."""
    await setup(dut)

    # 5 TX errors * 8 = 40
    for i in range(5):
        dut.tx_error.value = 1
        await RisingEdge(dut.clk)
        dut.tx_error.value = 0
        await RisingEdge(dut.clk)
        await RisingEdge(dut.clk)
    assert int(dut.tec.value) == 40, f"TEC should be 40, got {int(dut.tec.value)}"

    # 5 successful transmissions: TEC 40 -> 35
    dut.tx_active.value = 1
    for _ in range(5):
        dut.tx_done.value = 1
        await RisingEdge(dut.clk)
        dut.tx_done.value = 0
        await RisingEdge(dut.clk)
    assert int(dut.tec.value) == 35, f"TEC should be 35, got {int(dut.tec.value)}"

    # TEC must saturate at 0, no wrap-around
    for _ in range(40):
        dut.tx_done.value = 1
        await RisingEdge(dut.clk)
        dut.tx_done.value = 0
        await RisingEdge(dut.clk)
    assert int(dut.tec.value) == 0, f"TEC should saturate at 0, got {int(dut.tec.value)}"
    assert int(dut.state.value) == 0, "State should stay ERROR_ACTIVE"
    dut.tx_active.value = 0


@cocotb.test()
async def test_error_flag_generation(dut):
    """Active/passive error flags generated based on state."""
    await setup(dut)

    # ERROR_ACTIVE: error event drives the dominant active error flag
    dut.rx_error.value = 1
    await Timer(1, unit="ns")
    assert int(dut.error_flag_active.value) == 1, "active flag expected in ERROR_ACTIVE"
    assert int(dut.error_flag_passive.value) == 0, "passive flag must be off in ERROR_ACTIVE"
    dut.rx_error.value = 0
    await RisingEdge(dut.clk)

    # Move to ERROR_PASSIVE: 16 TX errors * 8 = 128
    for i in range(16):
        dut.tx_error.value = 1
        await RisingEdge(dut.clk)
        dut.tx_error.value = 0
        await RisingEdge(dut.clk)
        await RisingEdge(dut.clk)
    assert int(dut.state.value) == 1, "State should be ERROR_PASSIVE"

    # ERROR_PASSIVE: error event drives the recessive passive error flag
    dut.tx_error.value = 1
    await Timer(1, unit="ns")
    assert int(dut.error_flag_passive.value) == 1, "passive flag expected in ERROR_PASSIVE"
    assert int(dut.error_flag_active.value) == 0, "active flag must be off in ERROR_PASSIVE"
    dut.tx_error.value = 0
    await RisingEdge(dut.clk)
