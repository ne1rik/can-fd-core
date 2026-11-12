// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Symbol table implementation internals

#include "Vtop__pch.h"
#include "Vtop.h"
#include "Vtop___024root.h"

// FUNCTIONS
Vtop__Syms::~Vtop__Syms()
{

    // Tear down scope hierarchy
    __Vhier.remove(0, &__Vscope_crc17_canfd);

}

Vtop__Syms::Vtop__Syms(VerilatedContext* contextp, const char* namep, Vtop* modelp)
    : VerilatedSyms{contextp}
    // Setup internal state of the Syms class
    , __Vm_modelp{modelp}
    // Setup module instances
    , TOP{this, namep}
{
        // Check resources
        Verilated::stackCheck(33);
    // Configure time unit / time precision
    _vm_contextp__->timeunit(-9);
    _vm_contextp__->timeprecision(-12);
    // Setup each module's pointers to their submodules
    // Setup each module's pointer back to symbol table (for public functions)
    TOP.__Vconfigure(true);
    // Setup scopes
    __Vscope_TOP.configure(this, name(), "TOP", "TOP", "<null>", 0, VerilatedScope::SCOPE_OTHER);
    __Vscope_crc17_canfd.configure(this, name(), "crc17_canfd", "crc17_canfd", "crc17_canfd", -9, VerilatedScope::SCOPE_MODULE);

    // Set up scope hierarchy
    __Vhier.add(0, &__Vscope_crc17_canfd);

    // Setup export functions
    for (int __Vfinal = 0; __Vfinal < 2; ++__Vfinal) {
        __Vscope_TOP.varInsert(__Vfinal,"clk", &(TOP.clk), false, VLVT_UINT8,VLVD_IN|VLVF_PUB_RW,0,0);
        __Vscope_TOP.varInsert(__Vfinal,"crc_out", &(TOP.crc_out), false, VLVT_UINT32,VLVD_OUT|VLVF_PUB_RW,0,1 ,16,0);
        __Vscope_TOP.varInsert(__Vfinal,"crc_reset", &(TOP.crc_reset), false, VLVT_UINT8,VLVD_IN|VLVF_PUB_RW,0,0);
        __Vscope_TOP.varInsert(__Vfinal,"data_in", &(TOP.data_in), false, VLVT_UINT8,VLVD_IN|VLVF_PUB_RW,0,0);
        __Vscope_TOP.varInsert(__Vfinal,"data_in_valid", &(TOP.data_in_valid), false, VLVT_UINT8,VLVD_IN|VLVF_PUB_RW,0,0);
        __Vscope_TOP.varInsert(__Vfinal,"rst_n", &(TOP.rst_n), false, VLVT_UINT8,VLVD_IN|VLVF_PUB_RW,0,0);
        __Vscope_crc17_canfd.varInsert(__Vfinal,"MASK", const_cast<void*>(static_cast<const void*>(&(TOP.crc17_canfd__DOT__MASK))), true, VLVT_UINT32,VLVD_NODIR|VLVF_PUB_RW,0,1 ,16,0);
        __Vscope_crc17_canfd.varInsert(__Vfinal,"POLY", const_cast<void*>(static_cast<const void*>(&(TOP.crc17_canfd__DOT__POLY))), true, VLVT_UINT32,VLVD_NODIR|VLVF_PUB_RW,0,1 ,16,0);
        __Vscope_crc17_canfd.varInsert(__Vfinal,"clk", &(TOP.crc17_canfd__DOT__clk), false, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,0);
        __Vscope_crc17_canfd.varInsert(__Vfinal,"crc_out", &(TOP.crc17_canfd__DOT__crc_out), false, VLVT_UINT32,VLVD_NODIR|VLVF_PUB_RW,0,1 ,16,0);
        __Vscope_crc17_canfd.varInsert(__Vfinal,"crc_reg", &(TOP.crc17_canfd__DOT__crc_reg), false, VLVT_UINT32,VLVD_NODIR|VLVF_PUB_RW,0,1 ,16,0);
        __Vscope_crc17_canfd.varInsert(__Vfinal,"crc_reset", &(TOP.crc17_canfd__DOT__crc_reset), false, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,0);
        __Vscope_crc17_canfd.varInsert(__Vfinal,"data_in", &(TOP.crc17_canfd__DOT__data_in), false, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,0);
        __Vscope_crc17_canfd.varInsert(__Vfinal,"data_in_valid", &(TOP.crc17_canfd__DOT__data_in_valid), false, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,0);
        __Vscope_crc17_canfd.varInsert(__Vfinal,"rst_n", &(TOP.crc17_canfd__DOT__rst_n), false, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,0);
        __Vscope_crc17_canfd.varInsert(__Vfinal,"shifted", &(TOP.crc17_canfd__DOT__shifted), false, VLVT_UINT32,VLVD_NODIR|VLVF_PUB_RW,0,1 ,16,0);
    }
}
