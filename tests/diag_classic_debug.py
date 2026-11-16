"""Debug test: dump TX and RX bitstreams for one Classic CAN frame."""
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer

from can_fd_reference import generate_can_fd_frame


@cocotb.test()
async def test_classic_debug_one_frame(dut):
    """Dump TX and RX bitstreams for id=0x16b, dlc=7."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    
    # Reset
    dut.rst_n.value = 0
    dut.tx_start.value = 0
    dut.tx_data.value = 0
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)
    
    # Test vector: id=0x16b, dlc=7, data=[0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77]
    fid = 0x16b
    dlc = 7
    data = [0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77]
    
    # Generate expected bitstream via model
    expected_bits = generate_can_fd_frame(fid, dlc, data, False, extended=False, classic=True)
    
    cocotb.log.info(f"Expected bitstream ({len(expected_bits)} bits):")
    cocotb.log.info("".join(str(b) for b in expected_bits))
    
    # Capture TX bitstream
    tx_bits = []
    async def capture_tx():
        while True:
            await RisingEdge(dut.clk)
            if int(dut.tx_bit_valid.value) == 1:
                tx_bits.append(int(dut.tx_bit.value))
    
    cocotb.start_soon(capture_tx())
    
    # Send frame
    dut.tx_id.value = fid
    dut.tx_dlc.value = dlc
    dut.tx_brs.value = 0
    dut.tx_data.value = int.from_bytes(bytes(data), "big") << (512 - 8 * len(data))
    
    dut.tx_start.value = 1
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")
    dut.tx_start.value = 0
    
    # Wait for completion
    for _ in range(len(expected_bits) * 4 + 4000):
        await RisingEdge(dut.clk)
        await Timer(1, unit="ns")
        if int(dut.rx_done.value) == 1:
            break
    
    cocotb.log.info(f"TX bitstream ({len(tx_bits)} bits):")
    cocotb.log.info("".join(str(b) for b in tx_bits))
    
    # Compare
    cocotb.log.info(f"Expected len: {len(expected_bits)}, TX len: {len(tx_bits)}")
    if len(tx_bits) == len(expected_bits):
        mismatches = [(i, e, t) for i, (e, t) in enumerate(zip(expected_bits, tx_bits)) if e != t]
        if mismatches:
            cocotb.log.info(f"First 10 mismatches: {mismatches[:10]}")
        else:
            cocotb.log.info("TX matches expected!")
    
    # RX verdict
    cocotb.log.info(f"RX verdict: crc={int(dut.rx_crc_err.value)}, stuff={int(dut.rx_stuff_err.value)}, valid={int(dut.rx_valid.value)}")
