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
    VL_IN8(psel,0,0);
    VL_IN8(penable,0,0);
    VL_IN8(pwrite,0,0);
    VL_OUT8(pready,0,0);
    VL_OUT8(can_tx,0,0);
    VL_IN8(can_rx,0,0);
    VL_IN8(can_rx_error,0,0);
    VL_OUT8(can_tx_enable,0,0);
    CData/*0:0*/ can_fd_ctrl__DOT__clk;
    CData/*0:0*/ can_fd_ctrl__DOT__rst_n;
    CData/*0:0*/ can_fd_ctrl__DOT__psel;
    CData/*0:0*/ can_fd_ctrl__DOT__penable;
    CData/*0:0*/ can_fd_ctrl__DOT__pwrite;
    CData/*0:0*/ can_fd_ctrl__DOT__pready;
    CData/*0:0*/ can_fd_ctrl__DOT__can_tx;
    CData/*0:0*/ can_fd_ctrl__DOT__can_rx;
    CData/*0:0*/ can_fd_ctrl__DOT__can_rx_error;
    CData/*0:0*/ can_fd_ctrl__DOT__can_tx_enable;
    CData/*0:0*/ __VstlFirstIteration;
    CData/*0:0*/ __VicoFirstIteration;
    CData/*0:0*/ __Vtrigprevexpr___TOP__clk__0;
    CData/*0:0*/ __Vtrigprevexpr___TOP__rst_n__0;
    CData/*0:0*/ __VactContinue;
    VL_IN(paddr,31,0);
    VL_IN(pwdata,31,0);
    VL_OUT(prdata,31,0);
    IData/*31:0*/ can_fd_ctrl__DOT__paddr;
    IData/*31:0*/ can_fd_ctrl__DOT__pwdata;
    IData/*31:0*/ can_fd_ctrl__DOT__prdata;
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
