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
    VL_IN8(tx_start,0,0);
    VL_IN8(tx_dlc,3,0);
    VL_IN8(tx_brs,0,0);
    VL_OUT8(tx_bit,0,0);
    VL_OUT8(tx_bit_valid,0,0);
    VL_OUT8(tx_done,0,0);
    VL_OUT8(tx_busy,0,0);
    CData/*0:0*/ can_fd_tx__DOT__clk;
    CData/*0:0*/ can_fd_tx__DOT__rst_n;
    CData/*0:0*/ can_fd_tx__DOT__tx_start;
    CData/*3:0*/ can_fd_tx__DOT__tx_dlc;
    CData/*0:0*/ can_fd_tx__DOT__tx_brs;
    CData/*0:0*/ can_fd_tx__DOT__tx_bit;
    CData/*0:0*/ can_fd_tx__DOT__tx_bit_valid;
    CData/*0:0*/ can_fd_tx__DOT__tx_done;
    CData/*0:0*/ can_fd_tx__DOT__tx_busy;
    CData/*3:0*/ can_fd_tx__DOT__state;
    CData/*3:0*/ can_fd_tx__DOT__dlc_reg;
    CData/*0:0*/ can_fd_tx__DOT__brs_reg;
    CData/*2:0*/ can_fd_tx__DOT__run_cnt;
    CData/*0:0*/ can_fd_tx__DOT__run_bit;
    CData/*2:0*/ can_fd_tx__DOT__dyn;
    CData/*1:0*/ can_fd_tx__DOT__sc_idx;
    CData/*4:0*/ can_fd_tx__DOT__crc_idx;
    CData/*2:0*/ can_fd_tx__DOT__grp;
    CData/*3:0*/ can_fd_tx__DOT__tail_idx;
    CData/*0:0*/ can_fd_tx__DOT__is_crc21;
    CData/*4:0*/ can_fd_tx__DOT__cw;
    CData/*0:0*/ can_fd_tx__DOT__crc_step__Vstatic__m;
    CData/*6:0*/ can_fd_tx__DOT__data_bytes;
    CData/*2:0*/ can_fd_tx__DOT__gray;
    CData/*3:0*/ can_fd_tx__DOT__sc_field;
    CData/*0:0*/ can_fd_tx__DOT__raw_bit;
    CData/*0:0*/ __VstlFirstIteration;
    CData/*0:0*/ __VicoFirstIteration;
    CData/*0:0*/ __Vtrigprevexpr___TOP__clk__0;
    CData/*0:0*/ __Vtrigprevexpr___TOP__rst_n__0;
    CData/*0:0*/ __VactContinue;
    VL_IN16(tx_id,10,0);
    SData/*10:0*/ can_fd_tx__DOT__tx_id;
    SData/*10:0*/ can_fd_tx__DOT__id_reg;
    SData/*9:0*/ can_fd_tx__DOT__wr_len;
    SData/*9:0*/ can_fd_tx__DOT__rd_idx;
    SData/*9:0*/ can_fd_tx__DOT__raw_idx;
    SData/*9:0*/ can_fd_tx__DOT__raw_total;
    SData/*8:0*/ can_fd_tx__DOT__di;
    VL_INW(tx_data,511,0,16);
    VlWide<16>/*511:0*/ can_fd_tx__DOT__tx_data;
    VlWide<16>/*511:0*/ can_fd_tx__DOT__data_reg;
    IData/*20:0*/ can_fd_tx__DOT__crc_reg;
    IData/*20:0*/ can_fd_tx__DOT__crc_final;
    IData/*20:0*/ can_fd_tx__DOT__poly;
    IData/*20:0*/ can_fd_tx__DOT__cmask;
    IData/*20:0*/ can_fd_tx__DOT__crc_step__Vstatic__sh;
    IData/*31:0*/ __VactIterCount;
    VlUnpacked<CData/*0:0*/, 1024> can_fd_tx__DOT__frame_buf;
    VlTriggerVec<1> __VstlTriggered;
    VlTriggerVec<1> __VicoTriggered;
    VlTriggerVec<2> __VactTriggered;
    VlTriggerVec<2> __VnbaTriggered;

    // INTERNAL VARIABLES
    Vtop__Syms* const vlSymsp;

    // PARAMETERS
    static constexpr IData/*31:0*/ can_fd_tx__DOT__IDLE = 0U;
    static constexpr IData/*31:0*/ can_fd_tx__DOT__F_RAW = 1U;
    static constexpr IData/*31:0*/ can_fd_tx__DOT__F_STUFF = 2U;
    static constexpr IData/*31:0*/ can_fd_tx__DOT__F_FSB1 = 3U;
    static constexpr IData/*31:0*/ can_fd_tx__DOT__F_SC = 4U;
    static constexpr IData/*31:0*/ can_fd_tx__DOT__F_CRC = 5U;
    static constexpr IData/*31:0*/ can_fd_tx__DOT__F_TAIL = 6U;
    static constexpr IData/*31:0*/ can_fd_tx__DOT__F_SHIFT = 7U;
    static constexpr IData/*31:0*/ can_fd_tx__DOT__DONE = 8U;

    // CONSTRUCTORS
    Vtop___024root(Vtop__Syms* symsp, const char* v__name);
    ~Vtop___024root();
    VL_UNCOPYABLE(Vtop___024root);

    // INTERNAL METHODS
    void __Vconfigure(bool first);
};


#endif  // guard
