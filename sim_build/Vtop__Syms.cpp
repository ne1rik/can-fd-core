// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Symbol table implementation internals

#include "Vtop__pch.h"
#include "Vtop.h"
#include "Vtop___024root.h"

// FUNCTIONS
Vtop__Syms::~Vtop__Syms()
{

    // Tear down scope hierarchy
    __Vhier.remove(0, &__Vscope_can_fd_tx);

}

Vtop__Syms::Vtop__Syms(VerilatedContext* contextp, const char* namep, Vtop* modelp)
    : VerilatedSyms{contextp}
    // Setup internal state of the Syms class
    , __Vm_modelp{modelp}
    // Setup module instances
    , TOP{this, namep}
{
        // Check resources
        Verilated::stackCheck(201);
    // Configure time unit / time precision
    _vm_contextp__->timeunit(-9);
    _vm_contextp__->timeprecision(-12);
    // Setup each module's pointers to their submodules
    // Setup each module's pointer back to symbol table (for public functions)
    TOP.__Vconfigure(true);
    // Setup scopes
    __Vscope_TOP.configure(this, name(), "TOP", "TOP", "<null>", 0, VerilatedScope::SCOPE_OTHER);
    __Vscope_can_fd_tx.configure(this, name(), "can_fd_tx", "can_fd_tx", "can_fd_tx", -9, VerilatedScope::SCOPE_MODULE);

    // Set up scope hierarchy
    __Vhier.add(0, &__Vscope_can_fd_tx);

    // Setup export functions
    for (int __Vfinal = 0; __Vfinal < 2; ++__Vfinal) {
        __Vscope_TOP.varInsert(__Vfinal,"clk", &(TOP.clk), false, VLVT_UINT8,VLVD_IN|VLVF_PUB_RW,0,0);
        __Vscope_TOP.varInsert(__Vfinal,"rst_n", &(TOP.rst_n), false, VLVT_UINT8,VLVD_IN|VLVF_PUB_RW,0,0);
        __Vscope_TOP.varInsert(__Vfinal,"tx_bit", &(TOP.tx_bit), false, VLVT_UINT8,VLVD_OUT|VLVF_PUB_RW,0,0);
        __Vscope_TOP.varInsert(__Vfinal,"tx_bit_valid", &(TOP.tx_bit_valid), false, VLVT_UINT8,VLVD_OUT|VLVF_PUB_RW,0,0);
        __Vscope_TOP.varInsert(__Vfinal,"tx_brs", &(TOP.tx_brs), false, VLVT_UINT8,VLVD_IN|VLVF_PUB_RW,0,0);
        __Vscope_TOP.varInsert(__Vfinal,"tx_busy", &(TOP.tx_busy), false, VLVT_UINT8,VLVD_OUT|VLVF_PUB_RW,0,0);
        __Vscope_TOP.varInsert(__Vfinal,"tx_data", &(TOP.tx_data), false, VLVT_WDATA,VLVD_IN|VLVF_PUB_RW,0,1 ,511,0);
        __Vscope_TOP.varInsert(__Vfinal,"tx_dlc", &(TOP.tx_dlc), false, VLVT_UINT8,VLVD_IN|VLVF_PUB_RW,0,1 ,3,0);
        __Vscope_TOP.varInsert(__Vfinal,"tx_done", &(TOP.tx_done), false, VLVT_UINT8,VLVD_OUT|VLVF_PUB_RW,0,0);
        __Vscope_TOP.varInsert(__Vfinal,"tx_id", &(TOP.tx_id), false, VLVT_UINT16,VLVD_IN|VLVF_PUB_RW,0,1 ,10,0);
        __Vscope_TOP.varInsert(__Vfinal,"tx_start", &(TOP.tx_start), false, VLVT_UINT8,VLVD_IN|VLVF_PUB_RW,0,0);
        __Vscope_can_fd_tx.varInsert(__Vfinal,"DONE", const_cast<void*>(static_cast<const void*>(&(TOP.can_fd_tx__DOT__DONE))), true, VLVT_UINT32,VLVD_NODIR|VLVF_PUB_RW,0,1 ,31,0);
        __Vscope_can_fd_tx.varInsert(__Vfinal,"F_CRC", const_cast<void*>(static_cast<const void*>(&(TOP.can_fd_tx__DOT__F_CRC))), true, VLVT_UINT32,VLVD_NODIR|VLVF_PUB_RW,0,1 ,31,0);
        __Vscope_can_fd_tx.varInsert(__Vfinal,"F_FSB1", const_cast<void*>(static_cast<const void*>(&(TOP.can_fd_tx__DOT__F_FSB1))), true, VLVT_UINT32,VLVD_NODIR|VLVF_PUB_RW,0,1 ,31,0);
        __Vscope_can_fd_tx.varInsert(__Vfinal,"F_RAW", const_cast<void*>(static_cast<const void*>(&(TOP.can_fd_tx__DOT__F_RAW))), true, VLVT_UINT32,VLVD_NODIR|VLVF_PUB_RW,0,1 ,31,0);
        __Vscope_can_fd_tx.varInsert(__Vfinal,"F_SC", const_cast<void*>(static_cast<const void*>(&(TOP.can_fd_tx__DOT__F_SC))), true, VLVT_UINT32,VLVD_NODIR|VLVF_PUB_RW,0,1 ,31,0);
        __Vscope_can_fd_tx.varInsert(__Vfinal,"F_SHIFT", const_cast<void*>(static_cast<const void*>(&(TOP.can_fd_tx__DOT__F_SHIFT))), true, VLVT_UINT32,VLVD_NODIR|VLVF_PUB_RW,0,1 ,31,0);
        __Vscope_can_fd_tx.varInsert(__Vfinal,"F_STUFF", const_cast<void*>(static_cast<const void*>(&(TOP.can_fd_tx__DOT__F_STUFF))), true, VLVT_UINT32,VLVD_NODIR|VLVF_PUB_RW,0,1 ,31,0);
        __Vscope_can_fd_tx.varInsert(__Vfinal,"F_TAIL", const_cast<void*>(static_cast<const void*>(&(TOP.can_fd_tx__DOT__F_TAIL))), true, VLVT_UINT32,VLVD_NODIR|VLVF_PUB_RW,0,1 ,31,0);
        __Vscope_can_fd_tx.varInsert(__Vfinal,"IDLE", const_cast<void*>(static_cast<const void*>(&(TOP.can_fd_tx__DOT__IDLE))), true, VLVT_UINT32,VLVD_NODIR|VLVF_PUB_RW,0,1 ,31,0);
        __Vscope_can_fd_tx.varInsert(__Vfinal,"brs_reg", &(TOP.can_fd_tx__DOT__brs_reg), false, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,0);
        __Vscope_can_fd_tx.varInsert(__Vfinal,"clk", &(TOP.can_fd_tx__DOT__clk), false, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,0);
        __Vscope_can_fd_tx.varInsert(__Vfinal,"cmask", &(TOP.can_fd_tx__DOT__cmask), false, VLVT_UINT32,VLVD_NODIR|VLVF_PUB_RW,0,1 ,20,0);
        __Vscope_can_fd_tx.varInsert(__Vfinal,"crc_final", &(TOP.can_fd_tx__DOT__crc_final), false, VLVT_UINT32,VLVD_NODIR|VLVF_PUB_RW,0,1 ,20,0);
        __Vscope_can_fd_tx.varInsert(__Vfinal,"crc_idx", &(TOP.can_fd_tx__DOT__crc_idx), false, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,1 ,4,0);
        __Vscope_can_fd_tx.varInsert(__Vfinal,"crc_reg", &(TOP.can_fd_tx__DOT__crc_reg), false, VLVT_UINT32,VLVD_NODIR|VLVF_PUB_RW,0,1 ,20,0);
        __Vscope_can_fd_tx.varInsert(__Vfinal,"crc_step__Vstatic__m", &(TOP.can_fd_tx__DOT__crc_step__Vstatic__m), false, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,0);
        __Vscope_can_fd_tx.varInsert(__Vfinal,"crc_step__Vstatic__sh", &(TOP.can_fd_tx__DOT__crc_step__Vstatic__sh), false, VLVT_UINT32,VLVD_NODIR|VLVF_PUB_RW,0,1 ,20,0);
        __Vscope_can_fd_tx.varInsert(__Vfinal,"cw", &(TOP.can_fd_tx__DOT__cw), false, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,1 ,4,0);
        __Vscope_can_fd_tx.varInsert(__Vfinal,"data_bytes", &(TOP.can_fd_tx__DOT__data_bytes), false, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,1 ,6,0);
        __Vscope_can_fd_tx.varInsert(__Vfinal,"data_reg", &(TOP.can_fd_tx__DOT__data_reg), false, VLVT_WDATA,VLVD_NODIR|VLVF_PUB_RW,0,1 ,511,0);
        __Vscope_can_fd_tx.varInsert(__Vfinal,"di", &(TOP.can_fd_tx__DOT__di), false, VLVT_UINT16,VLVD_NODIR|VLVF_PUB_RW,0,1 ,8,0);
        __Vscope_can_fd_tx.varInsert(__Vfinal,"dlc_reg", &(TOP.can_fd_tx__DOT__dlc_reg), false, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,1 ,3,0);
        __Vscope_can_fd_tx.varInsert(__Vfinal,"dyn", &(TOP.can_fd_tx__DOT__dyn), false, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,1 ,2,0);
        __Vscope_can_fd_tx.varInsert(__Vfinal,"frame_buf", &(TOP.can_fd_tx__DOT__frame_buf), false, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,1,0 ,0,1023);
        __Vscope_can_fd_tx.varInsert(__Vfinal,"gray", &(TOP.can_fd_tx__DOT__gray), false, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,1 ,2,0);
        __Vscope_can_fd_tx.varInsert(__Vfinal,"grp", &(TOP.can_fd_tx__DOT__grp), false, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,1 ,2,0);
        __Vscope_can_fd_tx.varInsert(__Vfinal,"id_reg", &(TOP.can_fd_tx__DOT__id_reg), false, VLVT_UINT16,VLVD_NODIR|VLVF_PUB_RW,0,1 ,10,0);
        __Vscope_can_fd_tx.varInsert(__Vfinal,"is_crc21", &(TOP.can_fd_tx__DOT__is_crc21), false, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,0);
        __Vscope_can_fd_tx.varInsert(__Vfinal,"poly", &(TOP.can_fd_tx__DOT__poly), false, VLVT_UINT32,VLVD_NODIR|VLVF_PUB_RW,0,1 ,20,0);
        __Vscope_can_fd_tx.varInsert(__Vfinal,"raw_bit", &(TOP.can_fd_tx__DOT__raw_bit), false, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,0);
        __Vscope_can_fd_tx.varInsert(__Vfinal,"raw_idx", &(TOP.can_fd_tx__DOT__raw_idx), false, VLVT_UINT16,VLVD_NODIR|VLVF_PUB_RW,0,1 ,9,0);
        __Vscope_can_fd_tx.varInsert(__Vfinal,"raw_total", &(TOP.can_fd_tx__DOT__raw_total), false, VLVT_UINT16,VLVD_NODIR|VLVF_PUB_RW,0,1 ,9,0);
        __Vscope_can_fd_tx.varInsert(__Vfinal,"rd_idx", &(TOP.can_fd_tx__DOT__rd_idx), false, VLVT_UINT16,VLVD_NODIR|VLVF_PUB_RW,0,1 ,9,0);
        __Vscope_can_fd_tx.varInsert(__Vfinal,"rst_n", &(TOP.can_fd_tx__DOT__rst_n), false, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,0);
        __Vscope_can_fd_tx.varInsert(__Vfinal,"run_bit", &(TOP.can_fd_tx__DOT__run_bit), false, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,0);
        __Vscope_can_fd_tx.varInsert(__Vfinal,"run_cnt", &(TOP.can_fd_tx__DOT__run_cnt), false, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,1 ,2,0);
        __Vscope_can_fd_tx.varInsert(__Vfinal,"sc_field", &(TOP.can_fd_tx__DOT__sc_field), false, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,1 ,3,0);
        __Vscope_can_fd_tx.varInsert(__Vfinal,"sc_idx", &(TOP.can_fd_tx__DOT__sc_idx), false, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,1 ,1,0);
        __Vscope_can_fd_tx.varInsert(__Vfinal,"state", &(TOP.can_fd_tx__DOT__state), false, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,1 ,3,0);
        __Vscope_can_fd_tx.varInsert(__Vfinal,"tail_idx", &(TOP.can_fd_tx__DOT__tail_idx), false, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,1 ,3,0);
        __Vscope_can_fd_tx.varInsert(__Vfinal,"tx_bit", &(TOP.can_fd_tx__DOT__tx_bit), false, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,0);
        __Vscope_can_fd_tx.varInsert(__Vfinal,"tx_bit_valid", &(TOP.can_fd_tx__DOT__tx_bit_valid), false, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,0);
        __Vscope_can_fd_tx.varInsert(__Vfinal,"tx_brs", &(TOP.can_fd_tx__DOT__tx_brs), false, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,0);
        __Vscope_can_fd_tx.varInsert(__Vfinal,"tx_busy", &(TOP.can_fd_tx__DOT__tx_busy), false, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,0);
        __Vscope_can_fd_tx.varInsert(__Vfinal,"tx_data", &(TOP.can_fd_tx__DOT__tx_data), false, VLVT_WDATA,VLVD_NODIR|VLVF_PUB_RW,0,1 ,511,0);
        __Vscope_can_fd_tx.varInsert(__Vfinal,"tx_dlc", &(TOP.can_fd_tx__DOT__tx_dlc), false, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,1 ,3,0);
        __Vscope_can_fd_tx.varInsert(__Vfinal,"tx_done", &(TOP.can_fd_tx__DOT__tx_done), false, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,0);
        __Vscope_can_fd_tx.varInsert(__Vfinal,"tx_id", &(TOP.can_fd_tx__DOT__tx_id), false, VLVT_UINT16,VLVD_NODIR|VLVF_PUB_RW,0,1 ,10,0);
        __Vscope_can_fd_tx.varInsert(__Vfinal,"tx_start", &(TOP.can_fd_tx__DOT__tx_start), false, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,0);
        __Vscope_can_fd_tx.varInsert(__Vfinal,"wr_len", &(TOP.can_fd_tx__DOT__wr_len), false, VLVT_UINT16,VLVD_NODIR|VLVF_PUB_RW,0,1 ,9,0);
    }
}
