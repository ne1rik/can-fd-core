import cocotb, random
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer
from can_fd_reference import generate_can_fd_frame, dlc_len

async def run_frame(dut, fid, dlc, data, brs):
    # Ждём, пока DUT вернётся в IDLE (не busy и не done) — иначе стартовый
    # импульс попадает в DONE->IDLE и теряется.
    for _ in range(20):
        await RisingEdge(dut.clk); await Timer(1, unit="ns")
        if int(dut.tx_busy.value)==0 and int(dut.tx_done.value)==0:
            break
    dut.tx_id.value=fid; dut.tx_dlc.value=dlc; dut.tx_brs.value=brs
    n=dlc_len(dlc)
    dut.tx_data.value=(int.from_bytes(bytes(data[:n]),'big') << (512-8*n)) if n else 0
    dut.tx_start.value=1
    await RisingEdge(dut.clk); await Timer(1,unit="ns")
    dut.tx_start.value=0
    bits=[]; t=0
    while t<4000:
        await RisingEdge(dut.clk); await Timer(1,unit="ns")
        if int(dut.tx_bit_valid.value): bits.append(int(dut.tx_bit.value))
        if int(dut.tx_done.value): break
        t+=1
    ref=generate_can_fd_frame(fid,dlc,list(data[:n]),bool(brs))
    assert bits==ref, f"len {len(bits)} vs {len(ref)}; first diff at {next((i for i,(a,b) in enumerate(zip(bits,ref)) if a!=b),None)}"

async def init(dut):
    cocotb.start_soon(Clock(dut.clk,10,unit="ns").start())
    dut.rst_n.value=0; dut.tx_start.value=0
    await RisingEdge(dut.clk); await RisingEdge(dut.clk)
    dut.rst_n.value=1; await RisingEdge(dut.clk)

@cocotb.test()
async def t_anchor(dut):
    await init(dut); await run_frame(dut,0x5AA,8,[0xFF]*8,1)
@cocotb.test()
async def t_aa12(dut):
    await init(dut); await run_frame(dut,0x123,9,[0xAA]*12,1)
@cocotb.test()
async def t_zero12(dut):
    await init(dut); await run_frame(dut,0x123,9,[0x00]*12,1)
@cocotb.test()
async def t_ff64(dut):
    await init(dut); await run_frame(dut,0x7FF,15,[0xFF]*64,1)
@cocotb.test()
async def t_zero64(dut):
    await init(dut); await run_frame(dut,0x000,15,[0x00]*64,1)
@cocotb.test()
async def t_random(dut):
    await init(dut)
    for _ in range(5):
        dlc=random.randint(0,15)
        await run_frame(dut,random.randint(0,0x7FF),dlc,[random.randint(0,255) for _ in range(dlc_len(dlc))],random.randint(0,1))
