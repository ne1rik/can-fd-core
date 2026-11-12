// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design internal header
// See Vtop.h for the primary calling header

#ifndef VERILATED_VTOP___024ROOT_H_
#define VERILATED_VTOP___024ROOT_H_  // guard

#include "verilated.h"


class Vtop__Syms;

class alignas(VL_CACHE_LINE_BYTES) Vtop___024root final : public VerilatedModule {
  public:

    // DESIGN SPECIFIC STATE
    VL_IN8(clk,0,0);
    VL_IN8(rst_n,0,0);
    VL_IN8(data_in,0,0);
    VL_IN8(data_in_valid,0,0);
    VL_IN8(crc_reset,0,0);
    CData/*0:0*/ crc_canfd__DOT__clk;
    CData/*0:0*/ crc_canfd__DOT__rst_n;
    CData/*0:0*/ crc_canfd__DOT__data_in;
    CData/*0:0*/ crc_canfd__DOT__data_in_valid;
    CData/*0:0*/ crc_canfd__DOT__crc_reset;
    CData/*0:0*/ __VstlFirstIteration;
    CData/*0:0*/ __VicoFirstIteration;
    CData/*0:0*/ __Vtrigprevexpr___TOP__clk__0;
    CData/*0:0*/ __Vtrigprevexpr___TOP__rst_n__0;
    CData/*0:0*/ __VactContinue;
    VL_OUT(crc_out,20,0);
    IData/*20:0*/ crc_canfd__DOT__crc_out;
    IData/*20:0*/ crc_canfd__DOT__crc_reg;
    IData/*20:0*/ crc_canfd__DOT__shifted;
    IData/*20:0*/ crc_canfd__DOT__poly;
    IData/*31:0*/ __VactIterCount;
    VlTriggerVec<1> __VstlTriggered;
    VlTriggerVec<1> __VicoTriggered;
    VlTriggerVec<2> __VactTriggered;
    VlTriggerVec<2> __VnbaTriggered;

    // INTERNAL VARIABLES
    Vtop__Syms* const vlSymsp;

    // PARAMETERS
    static constexpr IData/*31:0*/ crc_canfd__DOT__CRC_WIDTH = 0x00000015U;
    static constexpr IData/*20:0*/ crc_canfd__DOT__POLY_17 = 0x0001685bU;
    static constexpr IData/*20:0*/ crc_canfd__DOT__POLY_21 = 0x00102899U;

    // CONSTRUCTORS
    Vtop___024root(Vtop__Syms* symsp, const char* v__name);
    ~Vtop___024root();
    VL_UNCOPYABLE(Vtop___024root);

    // INTERNAL METHODS
    void __Vconfigure(bool first);
};


#endif  // guard
