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
    VL_OUT8(data_out,0,0);
    VL_OUT8(data_out_valid,0,0);
    VL_OUT8(stuff_count,7,0);
    CData/*0:0*/ bit_stuffer__DOT__clk;
    CData/*0:0*/ bit_stuffer__DOT__rst_n;
    CData/*0:0*/ bit_stuffer__DOT__data_in;
    CData/*0:0*/ bit_stuffer__DOT__data_in_valid;
    CData/*0:0*/ bit_stuffer__DOT__data_out;
    CData/*0:0*/ bit_stuffer__DOT__data_out_valid;
    CData/*7:0*/ bit_stuffer__DOT__stuff_count;
    CData/*2:0*/ bit_stuffer__DOT__consecutive_count;
    CData/*0:0*/ bit_stuffer__DOT__last_bit;
    CData/*0:0*/ bit_stuffer__DOT__need_stuff_bit;
    CData/*0:0*/ bit_stuffer__DOT__first_bit;
    CData/*0:0*/ __VstlFirstIteration;
    CData/*0:0*/ __VicoFirstIteration;
    CData/*0:0*/ __Vtrigprevexpr___TOP__clk__0;
    CData/*0:0*/ __Vtrigprevexpr___TOP__rst_n__0;
    CData/*0:0*/ __VactContinue;
    IData/*31:0*/ __VactIterCount;
    VlTriggerVec<1> __VstlTriggered;
    VlTriggerVec<1> __VicoTriggered;
    VlTriggerVec<2> __VactTriggered;
    VlTriggerVec<2> __VnbaTriggered;

    // INTERNAL VARIABLES
    Vtop__Syms* const vlSymsp;

    // CONSTRUCTORS
    Vtop___024root(Vtop__Syms* symsp, const char* v__name);
    ~Vtop___024root();
    VL_UNCOPYABLE(Vtop___024root);

    // INTERNAL METHODS
    void __Vconfigure(bool first);
};


#endif  // guard
