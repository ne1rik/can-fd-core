// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design implementation internals
// See Vtop.h for the primary calling header

#include "Vtop__pch.h"
#include "Vtop___024root.h"

void Vtop___024root___ico_sequent__TOP__0(Vtop___024root* vlSelf);

void Vtop___024root___eval_ico(Vtop___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtop___024root___eval_ico\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if ((1ULL & vlSelfRef.__VicoTriggered.word(0U))) {
        Vtop___024root___ico_sequent__TOP__0(vlSelf);
    }
}

extern const VlUnpacked<CData/*6:0*/, 16> Vtop__ConstPool__TABLE_h2a89ce04_0;

VL_INLINE_OPT void Vtop___024root___ico_sequent__TOP__0(Vtop___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtop___024root___ico_sequent__TOP__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Init
    CData/*3:0*/ __Vtableidx1;
    __Vtableidx1 = 0;
    // Body
    vlSelfRef.can_fd_tx__DOT__clk = vlSelfRef.clk;
    vlSelfRef.can_fd_tx__DOT__rst_n = vlSelfRef.rst_n;
    vlSelfRef.can_fd_tx__DOT__tx_start = vlSelfRef.tx_start;
    vlSelfRef.can_fd_tx__DOT__tx_id = vlSelfRef.tx_id;
    vlSelfRef.can_fd_tx__DOT__tx_dlc = vlSelfRef.tx_dlc;
    vlSelfRef.can_fd_tx__DOT__tx_data[0U] = vlSelfRef.tx_data[0U];
    vlSelfRef.can_fd_tx__DOT__tx_data[1U] = vlSelfRef.tx_data[1U];
    vlSelfRef.can_fd_tx__DOT__tx_data[2U] = vlSelfRef.tx_data[2U];
    vlSelfRef.can_fd_tx__DOT__tx_data[3U] = vlSelfRef.tx_data[3U];
    vlSelfRef.can_fd_tx__DOT__tx_data[4U] = vlSelfRef.tx_data[4U];
    vlSelfRef.can_fd_tx__DOT__tx_data[5U] = vlSelfRef.tx_data[5U];
    vlSelfRef.can_fd_tx__DOT__tx_data[6U] = vlSelfRef.tx_data[6U];
    vlSelfRef.can_fd_tx__DOT__tx_data[7U] = vlSelfRef.tx_data[7U];
    vlSelfRef.can_fd_tx__DOT__tx_data[8U] = vlSelfRef.tx_data[8U];
    vlSelfRef.can_fd_tx__DOT__tx_data[9U] = vlSelfRef.tx_data[9U];
    vlSelfRef.can_fd_tx__DOT__tx_data[0xaU] = vlSelfRef.tx_data[0xaU];
    vlSelfRef.can_fd_tx__DOT__tx_data[0xbU] = vlSelfRef.tx_data[0xbU];
    vlSelfRef.can_fd_tx__DOT__tx_data[0xcU] = vlSelfRef.tx_data[0xcU];
    vlSelfRef.can_fd_tx__DOT__tx_data[0xdU] = vlSelfRef.tx_data[0xdU];
    vlSelfRef.can_fd_tx__DOT__tx_data[0xeU] = vlSelfRef.tx_data[0xeU];
    vlSelfRef.can_fd_tx__DOT__tx_data[0xfU] = vlSelfRef.tx_data[0xfU];
    vlSelfRef.can_fd_tx__DOT__tx_brs = vlSelfRef.tx_brs;
    vlSelfRef.tx_bit = vlSelfRef.can_fd_tx__DOT__tx_bit;
    vlSelfRef.tx_bit_valid = vlSelfRef.can_fd_tx__DOT__tx_bit_valid;
    vlSelfRef.can_fd_tx__DOT__tx_done = (8U == (IData)(vlSelfRef.can_fd_tx__DOT__state));
    vlSelfRef.can_fd_tx__DOT__tx_busy = ((0U != (IData)(vlSelfRef.can_fd_tx__DOT__state)) 
                                         & (8U != (IData)(vlSelfRef.can_fd_tx__DOT__state)));
    vlSelfRef.can_fd_tx__DOT__gray = (7U & ((IData)(vlSelfRef.can_fd_tx__DOT__dyn) 
                                            ^ VL_SHIFTR_III(3,3,32, (IData)(vlSelfRef.can_fd_tx__DOT__dyn), 1U)));
    __Vtableidx1 = vlSelfRef.can_fd_tx__DOT__dlc_reg;
    vlSelfRef.can_fd_tx__DOT__data_bytes = Vtop__ConstPool__TABLE_h2a89ce04_0
        [__Vtableidx1];
    vlSelfRef.can_fd_tx__DOT__di = (0x1ffU & ((IData)(vlSelfRef.can_fd_tx__DOT__raw_idx) 
                                              - (IData)(0x16U)));
    vlSelfRef.can_fd_tx__DOT__is_crc21 = (0xdU <= (IData)(vlSelfRef.can_fd_tx__DOT__dlc_reg));
    vlSelfRef.tx_done = vlSelfRef.can_fd_tx__DOT__tx_done;
    vlSelfRef.tx_busy = vlSelfRef.can_fd_tx__DOT__tx_busy;
    vlSelfRef.can_fd_tx__DOT__sc_field = (((IData)(vlSelfRef.can_fd_tx__DOT__gray) 
                                           << 1U) | 
                                          (1U & VL_REDXOR_4(vlSelfRef.can_fd_tx__DOT__gray)));
    vlSelfRef.can_fd_tx__DOT__raw_total = (0x3ffU & 
                                           ((IData)(0x16U) 
                                            + VL_SHIFTL_III(10,10,32, (IData)(vlSelfRef.can_fd_tx__DOT__data_bytes), 3U)));
    vlSelfRef.can_fd_tx__DOT__raw_bit = ((0U != (IData)(vlSelfRef.can_fd_tx__DOT__raw_idx)) 
                                         && (1U & (
                                                   (0xbU 
                                                    >= (IData)(vlSelfRef.can_fd_tx__DOT__raw_idx))
                                                    ? 
                                                   ((0xaU 
                                                     >= 
                                                     (0xfU 
                                                      & ((IData)(0xbU) 
                                                         - (IData)(vlSelfRef.can_fd_tx__DOT__raw_idx)))) 
                                                    && (1U 
                                                        & ((IData)(vlSelfRef.can_fd_tx__DOT__id_reg) 
                                                           >> 
                                                           (0xfU 
                                                            & ((IData)(0xbU) 
                                                               - (IData)(vlSelfRef.can_fd_tx__DOT__raw_idx))))))
                                                    : 
                                                   ((0x11U 
                                                     >= (IData)(vlSelfRef.can_fd_tx__DOT__raw_idx))
                                                     ? 
                                                    ((0xcU 
                                                      != (IData)(vlSelfRef.can_fd_tx__DOT__raw_idx)) 
                                                     && ((0xdU 
                                                          != (IData)(vlSelfRef.can_fd_tx__DOT__raw_idx)) 
                                                         && ((0xeU 
                                                              == (IData)(vlSelfRef.can_fd_tx__DOT__raw_idx)) 
                                                             || ((0xfU 
                                                                  != (IData)(vlSelfRef.can_fd_tx__DOT__raw_idx)) 
                                                                 && ((0x10U 
                                                                      == (IData)(vlSelfRef.can_fd_tx__DOT__raw_idx)) 
                                                                     && (IData)(vlSelfRef.can_fd_tx__DOT__brs_reg))))))
                                                     : 
                                                    ((0x15U 
                                                      >= (IData)(vlSelfRef.can_fd_tx__DOT__raw_idx))
                                                      ? 
                                                     ((0x12U 
                                                       == (IData)(vlSelfRef.can_fd_tx__DOT__raw_idx))
                                                       ? 
                                                      ((IData)(vlSelfRef.can_fd_tx__DOT__dlc_reg) 
                                                       >> 3U)
                                                       : 
                                                      ((0x13U 
                                                        == (IData)(vlSelfRef.can_fd_tx__DOT__raw_idx))
                                                        ? 
                                                       ((IData)(vlSelfRef.can_fd_tx__DOT__dlc_reg) 
                                                        >> 2U)
                                                        : 
                                                       ((0x14U 
                                                         == (IData)(vlSelfRef.can_fd_tx__DOT__raw_idx))
                                                         ? 
                                                        ((IData)(vlSelfRef.can_fd_tx__DOT__dlc_reg) 
                                                         >> 1U)
                                                         : 
                                                        ((0x15U 
                                                          == (IData)(vlSelfRef.can_fd_tx__DOT__raw_idx)) 
                                                         && (1U 
                                                             & (IData)(vlSelfRef.can_fd_tx__DOT__dlc_reg))))))
                                                      : 
                                                     (vlSelfRef.can_fd_tx__DOT__data_reg[
                                                      (0xfU 
                                                       & (((IData)(0x1ffU) 
                                                           - (IData)(vlSelfRef.can_fd_tx__DOT__di)) 
                                                          >> 5U))] 
                                                      >> 
                                                      (0x1fU 
                                                       & ((IData)(0x1ffU) 
                                                          - (IData)(vlSelfRef.can_fd_tx__DOT__di)))))))));
    if (vlSelfRef.can_fd_tx__DOT__is_crc21) {
        vlSelfRef.can_fd_tx__DOT__cmask = 0x1fffffU;
        vlSelfRef.can_fd_tx__DOT__poly = 0x102899U;
        vlSelfRef.can_fd_tx__DOT__cw = 0x15U;
    } else {
        vlSelfRef.can_fd_tx__DOT__cmask = 0x1ffffU;
        vlSelfRef.can_fd_tx__DOT__poly = 0x1685bU;
        vlSelfRef.can_fd_tx__DOT__cw = 0x11U;
    }
}

void Vtop___024root___eval_triggers__ico(Vtop___024root* vlSelf);

bool Vtop___024root___eval_phase__ico(Vtop___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtop___024root___eval_phase__ico\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Init
    CData/*0:0*/ __VicoExecute;
    // Body
    Vtop___024root___eval_triggers__ico(vlSelf);
    __VicoExecute = vlSelfRef.__VicoTriggered.any();
    if (__VicoExecute) {
        Vtop___024root___eval_ico(vlSelf);
    }
    return (__VicoExecute);
}

void Vtop___024root___eval_act(Vtop___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtop___024root___eval_act\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
}

void Vtop___024root___nba_sequent__TOP__0(Vtop___024root* vlSelf);

void Vtop___024root___eval_nba(Vtop___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtop___024root___eval_nba\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if ((3ULL & vlSelfRef.__VnbaTriggered.word(0U))) {
        Vtop___024root___nba_sequent__TOP__0(vlSelf);
    }
}

VL_INLINE_OPT void Vtop___024root___nba_sequent__TOP__0(Vtop___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtop___024root___nba_sequent__TOP__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Init
    IData/*20:0*/ __Vfunc_can_fd_tx__DOT__crc_step__0__Vfuncout;
    __Vfunc_can_fd_tx__DOT__crc_step__0__Vfuncout = 0;
    IData/*20:0*/ __Vfunc_can_fd_tx__DOT__crc_step__0__c;
    __Vfunc_can_fd_tx__DOT__crc_step__0__c = 0;
    CData/*0:0*/ __Vfunc_can_fd_tx__DOT__crc_step__0__b;
    __Vfunc_can_fd_tx__DOT__crc_step__0__b = 0;
    IData/*20:0*/ __Vfunc_can_fd_tx__DOT__crc_step__1__Vfuncout;
    __Vfunc_can_fd_tx__DOT__crc_step__1__Vfuncout = 0;
    IData/*20:0*/ __Vfunc_can_fd_tx__DOT__crc_step__1__c;
    __Vfunc_can_fd_tx__DOT__crc_step__1__c = 0;
    CData/*0:0*/ __Vfunc_can_fd_tx__DOT__crc_step__1__b;
    __Vfunc_can_fd_tx__DOT__crc_step__1__b = 0;
    IData/*20:0*/ __Vfunc_can_fd_tx__DOT__crc_step__2__Vfuncout;
    __Vfunc_can_fd_tx__DOT__crc_step__2__Vfuncout = 0;
    IData/*20:0*/ __Vfunc_can_fd_tx__DOT__crc_step__2__c;
    __Vfunc_can_fd_tx__DOT__crc_step__2__c = 0;
    CData/*0:0*/ __Vfunc_can_fd_tx__DOT__crc_step__2__b;
    __Vfunc_can_fd_tx__DOT__crc_step__2__b = 0;
    IData/*20:0*/ __Vfunc_can_fd_tx__DOT__crc_step__3__Vfuncout;
    __Vfunc_can_fd_tx__DOT__crc_step__3__Vfuncout = 0;
    IData/*20:0*/ __Vfunc_can_fd_tx__DOT__crc_step__3__c;
    __Vfunc_can_fd_tx__DOT__crc_step__3__c = 0;
    CData/*0:0*/ __Vfunc_can_fd_tx__DOT__crc_step__3__b;
    __Vfunc_can_fd_tx__DOT__crc_step__3__b = 0;
    CData/*3:0*/ __Vtableidx1;
    __Vtableidx1 = 0;
    SData/*9:0*/ __Vdly__can_fd_tx__DOT__wr_len;
    __Vdly__can_fd_tx__DOT__wr_len = 0;
    SData/*9:0*/ __Vdly__can_fd_tx__DOT__raw_idx;
    __Vdly__can_fd_tx__DOT__raw_idx = 0;
    CData/*2:0*/ __Vdly__can_fd_tx__DOT__run_cnt;
    __Vdly__can_fd_tx__DOT__run_cnt = 0;
    CData/*2:0*/ __Vdly__can_fd_tx__DOT__dyn;
    __Vdly__can_fd_tx__DOT__dyn = 0;
    IData/*20:0*/ __Vdly__can_fd_tx__DOT__crc_reg;
    __Vdly__can_fd_tx__DOT__crc_reg = 0;
    CData/*3:0*/ __Vdly__can_fd_tx__DOT__state;
    __Vdly__can_fd_tx__DOT__state = 0;
    CData/*0:0*/ __Vdly__can_fd_tx__DOT__run_bit;
    __Vdly__can_fd_tx__DOT__run_bit = 0;
    CData/*1:0*/ __Vdly__can_fd_tx__DOT__sc_idx;
    __Vdly__can_fd_tx__DOT__sc_idx = 0;
    CData/*4:0*/ __Vdly__can_fd_tx__DOT__crc_idx;
    __Vdly__can_fd_tx__DOT__crc_idx = 0;
    CData/*2:0*/ __Vdly__can_fd_tx__DOT__grp;
    __Vdly__can_fd_tx__DOT__grp = 0;
    IData/*20:0*/ __Vdly__can_fd_tx__DOT__crc_final;
    __Vdly__can_fd_tx__DOT__crc_final = 0;
    SData/*9:0*/ __Vdly__can_fd_tx__DOT__rd_idx;
    __Vdly__can_fd_tx__DOT__rd_idx = 0;
    CData/*3:0*/ __Vdly__can_fd_tx__DOT__tail_idx;
    __Vdly__can_fd_tx__DOT__tail_idx = 0;
    CData/*0:0*/ __VdlyVal__can_fd_tx__DOT__frame_buf__v0;
    __VdlyVal__can_fd_tx__DOT__frame_buf__v0 = 0;
    SData/*9:0*/ __VdlyDim0__can_fd_tx__DOT__frame_buf__v0;
    __VdlyDim0__can_fd_tx__DOT__frame_buf__v0 = 0;
    CData/*0:0*/ __VdlySet__can_fd_tx__DOT__frame_buf__v0;
    __VdlySet__can_fd_tx__DOT__frame_buf__v0 = 0;
    CData/*0:0*/ __VdlyVal__can_fd_tx__DOT__frame_buf__v1;
    __VdlyVal__can_fd_tx__DOT__frame_buf__v1 = 0;
    SData/*9:0*/ __VdlyDim0__can_fd_tx__DOT__frame_buf__v1;
    __VdlyDim0__can_fd_tx__DOT__frame_buf__v1 = 0;
    CData/*0:0*/ __VdlySet__can_fd_tx__DOT__frame_buf__v1;
    __VdlySet__can_fd_tx__DOT__frame_buf__v1 = 0;
    CData/*0:0*/ __VdlyVal__can_fd_tx__DOT__frame_buf__v2;
    __VdlyVal__can_fd_tx__DOT__frame_buf__v2 = 0;
    SData/*9:0*/ __VdlyDim0__can_fd_tx__DOT__frame_buf__v2;
    __VdlyDim0__can_fd_tx__DOT__frame_buf__v2 = 0;
    CData/*0:0*/ __VdlySet__can_fd_tx__DOT__frame_buf__v2;
    __VdlySet__can_fd_tx__DOT__frame_buf__v2 = 0;
    CData/*0:0*/ __VdlyVal__can_fd_tx__DOT__frame_buf__v3;
    __VdlyVal__can_fd_tx__DOT__frame_buf__v3 = 0;
    SData/*9:0*/ __VdlyDim0__can_fd_tx__DOT__frame_buf__v3;
    __VdlyDim0__can_fd_tx__DOT__frame_buf__v3 = 0;
    CData/*0:0*/ __VdlySet__can_fd_tx__DOT__frame_buf__v3;
    __VdlySet__can_fd_tx__DOT__frame_buf__v3 = 0;
    CData/*0:0*/ __VdlyVal__can_fd_tx__DOT__frame_buf__v4;
    __VdlyVal__can_fd_tx__DOT__frame_buf__v4 = 0;
    SData/*9:0*/ __VdlyDim0__can_fd_tx__DOT__frame_buf__v4;
    __VdlyDim0__can_fd_tx__DOT__frame_buf__v4 = 0;
    CData/*0:0*/ __VdlySet__can_fd_tx__DOT__frame_buf__v4;
    __VdlySet__can_fd_tx__DOT__frame_buf__v4 = 0;
    CData/*0:0*/ __VdlyVal__can_fd_tx__DOT__frame_buf__v5;
    __VdlyVal__can_fd_tx__DOT__frame_buf__v5 = 0;
    SData/*9:0*/ __VdlyDim0__can_fd_tx__DOT__frame_buf__v5;
    __VdlyDim0__can_fd_tx__DOT__frame_buf__v5 = 0;
    CData/*0:0*/ __VdlySet__can_fd_tx__DOT__frame_buf__v5;
    __VdlySet__can_fd_tx__DOT__frame_buf__v5 = 0;
    SData/*9:0*/ __VdlyDim0__can_fd_tx__DOT__frame_buf__v6;
    __VdlyDim0__can_fd_tx__DOT__frame_buf__v6 = 0;
    CData/*0:0*/ __VdlySet__can_fd_tx__DOT__frame_buf__v6;
    __VdlySet__can_fd_tx__DOT__frame_buf__v6 = 0;
    // Body
    __Vdly__can_fd_tx__DOT__wr_len = vlSelfRef.can_fd_tx__DOT__wr_len;
    __Vdly__can_fd_tx__DOT__run_cnt = vlSelfRef.can_fd_tx__DOT__run_cnt;
    __Vdly__can_fd_tx__DOT__crc_reg = vlSelfRef.can_fd_tx__DOT__crc_reg;
    __Vdly__can_fd_tx__DOT__run_bit = vlSelfRef.can_fd_tx__DOT__run_bit;
    __Vdly__can_fd_tx__DOT__sc_idx = vlSelfRef.can_fd_tx__DOT__sc_idx;
    __Vdly__can_fd_tx__DOT__crc_idx = vlSelfRef.can_fd_tx__DOT__crc_idx;
    __Vdly__can_fd_tx__DOT__grp = vlSelfRef.can_fd_tx__DOT__grp;
    __Vdly__can_fd_tx__DOT__crc_final = vlSelfRef.can_fd_tx__DOT__crc_final;
    __Vdly__can_fd_tx__DOT__rd_idx = vlSelfRef.can_fd_tx__DOT__rd_idx;
    __Vdly__can_fd_tx__DOT__tail_idx = vlSelfRef.can_fd_tx__DOT__tail_idx;
    __Vdly__can_fd_tx__DOT__dyn = vlSelfRef.can_fd_tx__DOT__dyn;
    __Vdly__can_fd_tx__DOT__state = vlSelfRef.can_fd_tx__DOT__state;
    __Vdly__can_fd_tx__DOT__raw_idx = vlSelfRef.can_fd_tx__DOT__raw_idx;
    __VdlySet__can_fd_tx__DOT__frame_buf__v0 = 0U;
    __VdlySet__can_fd_tx__DOT__frame_buf__v1 = 0U;
    __VdlySet__can_fd_tx__DOT__frame_buf__v2 = 0U;
    __VdlySet__can_fd_tx__DOT__frame_buf__v3 = 0U;
    __VdlySet__can_fd_tx__DOT__frame_buf__v4 = 0U;
    __VdlySet__can_fd_tx__DOT__frame_buf__v5 = 0U;
    __VdlySet__can_fd_tx__DOT__frame_buf__v6 = 0U;
    if (vlSelfRef.rst_n) {
        vlSelfRef.can_fd_tx__DOT__tx_bit_valid = 0U;
        if (((((((((0U == (IData)(vlSelfRef.can_fd_tx__DOT__state)) 
                   | (1U == (IData)(vlSelfRef.can_fd_tx__DOT__state))) 
                  | (2U == (IData)(vlSelfRef.can_fd_tx__DOT__state))) 
                 | (3U == (IData)(vlSelfRef.can_fd_tx__DOT__state))) 
                | (4U == (IData)(vlSelfRef.can_fd_tx__DOT__state))) 
               | (5U == (IData)(vlSelfRef.can_fd_tx__DOT__state))) 
              | (6U == (IData)(vlSelfRef.can_fd_tx__DOT__state))) 
             | (7U == (IData)(vlSelfRef.can_fd_tx__DOT__state)))) {
            if ((0U == (IData)(vlSelfRef.can_fd_tx__DOT__state))) {
                if (vlSelfRef.tx_start) {
                    vlSelfRef.can_fd_tx__DOT__id_reg 
                        = vlSelfRef.tx_id;
                    vlSelfRef.can_fd_tx__DOT__dlc_reg 
                        = vlSelfRef.tx_dlc;
                    vlSelfRef.can_fd_tx__DOT__data_reg[0U] 
                        = vlSelfRef.tx_data[0U];
                    vlSelfRef.can_fd_tx__DOT__data_reg[1U] 
                        = vlSelfRef.tx_data[1U];
                    vlSelfRef.can_fd_tx__DOT__data_reg[2U] 
                        = vlSelfRef.tx_data[2U];
                    vlSelfRef.can_fd_tx__DOT__data_reg[3U] 
                        = vlSelfRef.tx_data[3U];
                    vlSelfRef.can_fd_tx__DOT__data_reg[4U] 
                        = vlSelfRef.tx_data[4U];
                    vlSelfRef.can_fd_tx__DOT__data_reg[5U] 
                        = vlSelfRef.tx_data[5U];
                    vlSelfRef.can_fd_tx__DOT__data_reg[6U] 
                        = vlSelfRef.tx_data[6U];
                    vlSelfRef.can_fd_tx__DOT__data_reg[7U] 
                        = vlSelfRef.tx_data[7U];
                    vlSelfRef.can_fd_tx__DOT__data_reg[8U] 
                        = vlSelfRef.tx_data[8U];
                    vlSelfRef.can_fd_tx__DOT__data_reg[9U] 
                        = vlSelfRef.tx_data[9U];
                    vlSelfRef.can_fd_tx__DOT__data_reg[0xaU] 
                        = vlSelfRef.tx_data[0xaU];
                    vlSelfRef.can_fd_tx__DOT__data_reg[0xbU] 
                        = vlSelfRef.tx_data[0xbU];
                    vlSelfRef.can_fd_tx__DOT__data_reg[0xcU] 
                        = vlSelfRef.tx_data[0xcU];
                    vlSelfRef.can_fd_tx__DOT__data_reg[0xdU] 
                        = vlSelfRef.tx_data[0xdU];
                    vlSelfRef.can_fd_tx__DOT__data_reg[0xeU] 
                        = vlSelfRef.tx_data[0xeU];
                    vlSelfRef.can_fd_tx__DOT__data_reg[0xfU] 
                        = vlSelfRef.tx_data[0xfU];
                    vlSelfRef.can_fd_tx__DOT__brs_reg 
                        = vlSelfRef.tx_brs;
                    __Vdly__can_fd_tx__DOT__wr_len = 0U;
                    __Vdly__can_fd_tx__DOT__raw_idx = 0U;
                    __Vdly__can_fd_tx__DOT__run_cnt = 0U;
                    __Vdly__can_fd_tx__DOT__dyn = 0U;
                    __Vdly__can_fd_tx__DOT__crc_reg 
                        = ((0xdU <= (IData)(vlSelfRef.tx_dlc))
                            ? 0x100000U : 0x10000U);
                    __Vdly__can_fd_tx__DOT__state = 1U;
                }
            } else if ((1U == (IData)(vlSelfRef.can_fd_tx__DOT__state))) {
                __Vfunc_can_fd_tx__DOT__crc_step__0__b 
                    = vlSelfRef.can_fd_tx__DOT__raw_bit;
                __Vfunc_can_fd_tx__DOT__crc_step__0__c 
                    = vlSelfRef.can_fd_tx__DOT__crc_reg;
                __VdlyVal__can_fd_tx__DOT__frame_buf__v0 
                    = vlSelfRef.can_fd_tx__DOT__raw_bit;
                __VdlyDim0__can_fd_tx__DOT__frame_buf__v0 
                    = vlSelfRef.can_fd_tx__DOT__wr_len;
                __VdlySet__can_fd_tx__DOT__frame_buf__v0 = 1U;
                vlSelfRef.can_fd_tx__DOT__crc_step__Vstatic__m 
                    = (1U & ((IData)(vlSelfRef.can_fd_tx__DOT__is_crc21)
                              ? (__Vfunc_can_fd_tx__DOT__crc_step__0__c 
                                 >> 0x14U) : (__Vfunc_can_fd_tx__DOT__crc_step__0__c 
                                              >> 0x10U)));
                if ((((0U != (IData)(vlSelfRef.can_fd_tx__DOT__run_cnt)) 
                      & ((IData)(vlSelfRef.can_fd_tx__DOT__raw_bit) 
                         == (IData)(vlSelfRef.can_fd_tx__DOT__run_bit))) 
                     & (4U == (IData)(vlSelfRef.can_fd_tx__DOT__run_cnt)))) {
                    __Vdly__can_fd_tx__DOT__raw_idx 
                        = (0x3ffU & ((IData)(1U) + (IData)(vlSelfRef.can_fd_tx__DOT__raw_idx)));
                    __Vdly__can_fd_tx__DOT__run_bit 
                        = (1U & (~ (IData)(vlSelfRef.can_fd_tx__DOT__raw_bit)));
                    __Vdly__can_fd_tx__DOT__run_cnt = 1U;
                    __Vdly__can_fd_tx__DOT__state = 2U;
                } else {
                    if (((0U == (IData)(vlSelfRef.can_fd_tx__DOT__run_cnt)) 
                         | ((IData)(vlSelfRef.can_fd_tx__DOT__raw_bit) 
                            != (IData)(vlSelfRef.can_fd_tx__DOT__run_bit)))) {
                        __Vdly__can_fd_tx__DOT__run_bit 
                            = vlSelfRef.can_fd_tx__DOT__raw_bit;
                        __Vdly__can_fd_tx__DOT__run_cnt = 1U;
                    } else {
                        __Vdly__can_fd_tx__DOT__run_cnt 
                            = (7U & ((IData)(1U) + (IData)(vlSelfRef.can_fd_tx__DOT__run_cnt)));
                    }
                    __Vdly__can_fd_tx__DOT__raw_idx 
                        = (0x3ffU & ((IData)(1U) + (IData)(vlSelfRef.can_fd_tx__DOT__raw_idx)));
                    if ((((IData)(1U) + (IData)(vlSelfRef.can_fd_tx__DOT__raw_idx)) 
                         == (IData)(vlSelfRef.can_fd_tx__DOT__raw_total))) {
                        __Vdly__can_fd_tx__DOT__state = 3U;
                    }
                }
                __Vdly__can_fd_tx__DOT__wr_len = (0x3ffU 
                                                  & ((IData)(1U) 
                                                     + (IData)(vlSelfRef.can_fd_tx__DOT__wr_len)));
                vlSelfRef.can_fd_tx__DOT__crc_step__Vstatic__sh 
                    = (VL_SHIFTL_III(21,21,32, __Vfunc_can_fd_tx__DOT__crc_step__0__c, 1U) 
                       & vlSelfRef.can_fd_tx__DOT__cmask);
                __Vfunc_can_fd_tx__DOT__crc_step__0__Vfuncout 
                    = (((IData)(vlSelfRef.can_fd_tx__DOT__crc_step__Vstatic__m) 
                        ^ (IData)(__Vfunc_can_fd_tx__DOT__crc_step__0__b))
                        ? (vlSelfRef.can_fd_tx__DOT__crc_step__Vstatic__sh 
                           ^ vlSelfRef.can_fd_tx__DOT__poly)
                        : vlSelfRef.can_fd_tx__DOT__crc_step__Vstatic__sh);
                __Vdly__can_fd_tx__DOT__crc_reg = __Vfunc_can_fd_tx__DOT__crc_step__0__Vfuncout;
            } else if ((2U == (IData)(vlSelfRef.can_fd_tx__DOT__state))) {
                __VdlyVal__can_fd_tx__DOT__frame_buf__v1 
                    = vlSelfRef.can_fd_tx__DOT__run_bit;
                __VdlyDim0__can_fd_tx__DOT__frame_buf__v1 
                    = vlSelfRef.can_fd_tx__DOT__wr_len;
                __VdlySet__can_fd_tx__DOT__frame_buf__v1 = 1U;
                __Vdly__can_fd_tx__DOT__wr_len = (0x3ffU 
                                                  & ((IData)(1U) 
                                                     + (IData)(vlSelfRef.can_fd_tx__DOT__wr_len)));
                if (((IData)(vlSelfRef.can_fd_tx__DOT__raw_idx) 
                     == (IData)(vlSelfRef.can_fd_tx__DOT__raw_total))) {
                    __Vdly__can_fd_tx__DOT__state = 4U;
                    __Vdly__can_fd_tx__DOT__sc_idx = 0U;
                } else {
                    __Vfunc_can_fd_tx__DOT__crc_step__1__b 
                        = vlSelfRef.can_fd_tx__DOT__run_bit;
                    __Vdly__can_fd_tx__DOT__dyn = (7U 
                                                   & ((IData)(1U) 
                                                      + (IData)(vlSelfRef.can_fd_tx__DOT__dyn)));
                    __Vfunc_can_fd_tx__DOT__crc_step__1__c 
                        = vlSelfRef.can_fd_tx__DOT__crc_reg;
                    vlSelfRef.can_fd_tx__DOT__crc_step__Vstatic__m 
                        = (1U & ((IData)(vlSelfRef.can_fd_tx__DOT__is_crc21)
                                  ? (__Vfunc_can_fd_tx__DOT__crc_step__1__c 
                                     >> 0x14U) : (__Vfunc_can_fd_tx__DOT__crc_step__1__c 
                                                  >> 0x10U)));
                    __Vdly__can_fd_tx__DOT__state = 1U;
                    vlSelfRef.can_fd_tx__DOT__crc_step__Vstatic__sh 
                        = (VL_SHIFTL_III(21,21,32, __Vfunc_can_fd_tx__DOT__crc_step__1__c, 1U) 
                           & vlSelfRef.can_fd_tx__DOT__cmask);
                    __Vfunc_can_fd_tx__DOT__crc_step__1__Vfuncout 
                        = (((IData)(vlSelfRef.can_fd_tx__DOT__crc_step__Vstatic__m) 
                            ^ (IData)(__Vfunc_can_fd_tx__DOT__crc_step__1__b))
                            ? (vlSelfRef.can_fd_tx__DOT__crc_step__Vstatic__sh 
                               ^ vlSelfRef.can_fd_tx__DOT__poly)
                            : vlSelfRef.can_fd_tx__DOT__crc_step__Vstatic__sh);
                    __Vdly__can_fd_tx__DOT__crc_reg 
                        = __Vfunc_can_fd_tx__DOT__crc_step__1__Vfuncout;
                }
            } else if ((3U == (IData)(vlSelfRef.can_fd_tx__DOT__state))) {
                __VdlyVal__can_fd_tx__DOT__frame_buf__v2 
                    = (1U & (~ vlSelfRef.can_fd_tx__DOT__frame_buf
                             [(0x3ffU & ((IData)(vlSelfRef.can_fd_tx__DOT__wr_len) 
                                         - (IData)(1U)))]));
                __VdlyDim0__can_fd_tx__DOT__frame_buf__v2 
                    = vlSelfRef.can_fd_tx__DOT__wr_len;
                __VdlySet__can_fd_tx__DOT__frame_buf__v2 = 1U;
                __Vdly__can_fd_tx__DOT__wr_len = (0x3ffU 
                                                  & ((IData)(1U) 
                                                     + (IData)(vlSelfRef.can_fd_tx__DOT__wr_len)));
                __Vdly__can_fd_tx__DOT__state = 4U;
                __Vdly__can_fd_tx__DOT__sc_idx = 0U;
            } else if ((4U == (IData)(vlSelfRef.can_fd_tx__DOT__state))) {
                __VdlyVal__can_fd_tx__DOT__frame_buf__v3 
                    = (1U & ((IData)(vlSelfRef.can_fd_tx__DOT__sc_field) 
                             >> (3U & ((IData)(3U) 
                                       - (IData)(vlSelfRef.can_fd_tx__DOT__sc_idx)))));
                __VdlyDim0__can_fd_tx__DOT__frame_buf__v3 
                    = vlSelfRef.can_fd_tx__DOT__wr_len;
                __VdlySet__can_fd_tx__DOT__frame_buf__v3 = 1U;
                __Vdly__can_fd_tx__DOT__wr_len = (0x3ffU 
                                                  & ((IData)(1U) 
                                                     + (IData)(vlSelfRef.can_fd_tx__DOT__wr_len)));
                __Vfunc_can_fd_tx__DOT__crc_step__2__b 
                    = (1U & ((IData)(vlSelfRef.can_fd_tx__DOT__sc_field) 
                             >> (3U & ((IData)(3U) 
                                       - (IData)(vlSelfRef.can_fd_tx__DOT__sc_idx)))));
                __Vfunc_can_fd_tx__DOT__crc_step__2__c 
                    = vlSelfRef.can_fd_tx__DOT__crc_reg;
                vlSelfRef.can_fd_tx__DOT__crc_step__Vstatic__m 
                    = (1U & ((IData)(vlSelfRef.can_fd_tx__DOT__is_crc21)
                              ? (__Vfunc_can_fd_tx__DOT__crc_step__2__c 
                                 >> 0x14U) : (__Vfunc_can_fd_tx__DOT__crc_step__2__c 
                                              >> 0x10U)));
                vlSelfRef.can_fd_tx__DOT__crc_step__Vstatic__sh 
                    = (VL_SHIFTL_III(21,21,32, __Vfunc_can_fd_tx__DOT__crc_step__2__c, 1U) 
                       & vlSelfRef.can_fd_tx__DOT__cmask);
                __Vfunc_can_fd_tx__DOT__crc_step__2__Vfuncout 
                    = (((IData)(vlSelfRef.can_fd_tx__DOT__crc_step__Vstatic__m) 
                        ^ (IData)(__Vfunc_can_fd_tx__DOT__crc_step__2__b))
                        ? (vlSelfRef.can_fd_tx__DOT__crc_step__Vstatic__sh 
                           ^ vlSelfRef.can_fd_tx__DOT__poly)
                        : vlSelfRef.can_fd_tx__DOT__crc_step__Vstatic__sh);
                __Vdly__can_fd_tx__DOT__crc_reg = __Vfunc_can_fd_tx__DOT__crc_step__2__Vfuncout;
                if ((3U == (IData)(vlSelfRef.can_fd_tx__DOT__sc_idx))) {
                    __Vfunc_can_fd_tx__DOT__crc_step__3__b 
                        = (1U & ((IData)(vlSelfRef.can_fd_tx__DOT__sc_field) 
                                 >> (3U & ((IData)(3U) 
                                           - (IData)(vlSelfRef.can_fd_tx__DOT__sc_idx)))));
                    __Vfunc_can_fd_tx__DOT__crc_step__3__c 
                        = vlSelfRef.can_fd_tx__DOT__crc_reg;
                    vlSelfRef.can_fd_tx__DOT__crc_step__Vstatic__m 
                        = (1U & ((IData)(vlSelfRef.can_fd_tx__DOT__is_crc21)
                                  ? (__Vfunc_can_fd_tx__DOT__crc_step__3__c 
                                     >> 0x14U) : (__Vfunc_can_fd_tx__DOT__crc_step__3__c 
                                                  >> 0x10U)));
                    __Vdly__can_fd_tx__DOT__state = 5U;
                    __Vdly__can_fd_tx__DOT__crc_idx = 0U;
                    __Vdly__can_fd_tx__DOT__grp = 0U;
                    vlSelfRef.can_fd_tx__DOT__crc_step__Vstatic__sh 
                        = (VL_SHIFTL_III(21,21,32, __Vfunc_can_fd_tx__DOT__crc_step__3__c, 1U) 
                           & vlSelfRef.can_fd_tx__DOT__cmask);
                    __Vfunc_can_fd_tx__DOT__crc_step__3__Vfuncout 
                        = (((IData)(vlSelfRef.can_fd_tx__DOT__crc_step__Vstatic__m) 
                            ^ (IData)(__Vfunc_can_fd_tx__DOT__crc_step__3__b))
                            ? (vlSelfRef.can_fd_tx__DOT__crc_step__Vstatic__sh 
                               ^ vlSelfRef.can_fd_tx__DOT__poly)
                            : vlSelfRef.can_fd_tx__DOT__crc_step__Vstatic__sh);
                    __Vdly__can_fd_tx__DOT__crc_final 
                        = __Vfunc_can_fd_tx__DOT__crc_step__3__Vfuncout;
                } else {
                    __Vdly__can_fd_tx__DOT__sc_idx 
                        = (3U & ((IData)(1U) + (IData)(vlSelfRef.can_fd_tx__DOT__sc_idx)));
                }
            } else if ((5U == (IData)(vlSelfRef.can_fd_tx__DOT__state))) {
                if ((0U == (IData)(vlSelfRef.can_fd_tx__DOT__grp))) {
                    __VdlyVal__can_fd_tx__DOT__frame_buf__v4 
                        = (1U & (~ vlSelfRef.can_fd_tx__DOT__frame_buf
                                 [(0x3ffU & ((IData)(vlSelfRef.can_fd_tx__DOT__wr_len) 
                                             - (IData)(1U)))]));
                    __VdlyDim0__can_fd_tx__DOT__frame_buf__v4 
                        = vlSelfRef.can_fd_tx__DOT__wr_len;
                    __VdlySet__can_fd_tx__DOT__frame_buf__v4 = 1U;
                    __Vdly__can_fd_tx__DOT__wr_len 
                        = (0x3ffU & ((IData)(1U) + (IData)(vlSelfRef.can_fd_tx__DOT__wr_len)));
                    __Vdly__can_fd_tx__DOT__grp = 1U;
                } else {
                    __VdlyVal__can_fd_tx__DOT__frame_buf__v5 
                        = ((0x14U >= (0x1fU & (((IData)(vlSelfRef.can_fd_tx__DOT__cw) 
                                                - (IData)(1U)) 
                                               - (IData)(vlSelfRef.can_fd_tx__DOT__crc_idx)))) 
                           && (1U & (vlSelfRef.can_fd_tx__DOT__crc_final 
                                     >> (0x1fU & (((IData)(vlSelfRef.can_fd_tx__DOT__cw) 
                                                   - (IData)(1U)) 
                                                  - (IData)(vlSelfRef.can_fd_tx__DOT__crc_idx))))));
                    __VdlyDim0__can_fd_tx__DOT__frame_buf__v5 
                        = vlSelfRef.can_fd_tx__DOT__wr_len;
                    __VdlySet__can_fd_tx__DOT__frame_buf__v5 = 1U;
                    __Vdly__can_fd_tx__DOT__wr_len 
                        = (0x3ffU & ((IData)(1U) + (IData)(vlSelfRef.can_fd_tx__DOT__wr_len)));
                    __Vdly__can_fd_tx__DOT__crc_idx 
                        = (0x1fU & ((IData)(1U) + (IData)(vlSelfRef.can_fd_tx__DOT__crc_idx)));
                    if ((((IData)(1U) + (IData)(vlSelfRef.can_fd_tx__DOT__crc_idx)) 
                         == (IData)(vlSelfRef.can_fd_tx__DOT__cw))) {
                        __Vdly__can_fd_tx__DOT__state = 6U;
                    } else {
                        __Vdly__can_fd_tx__DOT__grp 
                            = ((4U == (IData)(vlSelfRef.can_fd_tx__DOT__grp))
                                ? 0U : (7U & ((IData)(1U) 
                                              + (IData)(vlSelfRef.can_fd_tx__DOT__grp))));
                    }
                }
            } else if ((6U == (IData)(vlSelfRef.can_fd_tx__DOT__state))) {
                __VdlyDim0__can_fd_tx__DOT__frame_buf__v6 
                    = vlSelfRef.can_fd_tx__DOT__wr_len;
                __VdlySet__can_fd_tx__DOT__frame_buf__v6 = 1U;
                if ((9U == (IData)(vlSelfRef.can_fd_tx__DOT__tail_idx))) {
                    __Vdly__can_fd_tx__DOT__state = 7U;
                    __Vdly__can_fd_tx__DOT__rd_idx = 0U;
                    __Vdly__can_fd_tx__DOT__tail_idx = 0U;
                } else {
                    __Vdly__can_fd_tx__DOT__tail_idx 
                        = (0xfU & ((IData)(1U) + (IData)(vlSelfRef.can_fd_tx__DOT__tail_idx)));
                }
                __Vdly__can_fd_tx__DOT__wr_len = (0x3ffU 
                                                  & ((IData)(1U) 
                                                     + (IData)(vlSelfRef.can_fd_tx__DOT__wr_len)));
            } else if (((IData)(vlSelfRef.can_fd_tx__DOT__rd_idx) 
                        < (IData)(vlSelfRef.can_fd_tx__DOT__wr_len))) {
                vlSelfRef.can_fd_tx__DOT__tx_bit = 
                    vlSelfRef.can_fd_tx__DOT__frame_buf
                    [vlSelfRef.can_fd_tx__DOT__rd_idx];
                vlSelfRef.can_fd_tx__DOT__tx_bit_valid = 1U;
                __Vdly__can_fd_tx__DOT__rd_idx = (0x3ffU 
                                                  & ((IData)(1U) 
                                                     + (IData)(vlSelfRef.can_fd_tx__DOT__rd_idx)));
            } else {
                __Vdly__can_fd_tx__DOT__state = 8U;
            }
        } else {
            __Vdly__can_fd_tx__DOT__state = 0U;
        }
    } else {
        __Vdly__can_fd_tx__DOT__tail_idx = 0U;
        __Vdly__can_fd_tx__DOT__state = 0U;
        vlSelfRef.can_fd_tx__DOT__tx_bit = 1U;
        vlSelfRef.can_fd_tx__DOT__tx_bit_valid = 0U;
        __Vdly__can_fd_tx__DOT__wr_len = 0U;
        __Vdly__can_fd_tx__DOT__rd_idx = 0U;
        __Vdly__can_fd_tx__DOT__raw_idx = 0U;
        __Vdly__can_fd_tx__DOT__run_cnt = 0U;
        __Vdly__can_fd_tx__DOT__run_bit = 0U;
        __Vdly__can_fd_tx__DOT__dyn = 0U;
        __Vdly__can_fd_tx__DOT__crc_reg = 0U;
        __Vdly__can_fd_tx__DOT__crc_final = 0U;
        __Vdly__can_fd_tx__DOT__sc_idx = 0U;
        __Vdly__can_fd_tx__DOT__crc_idx = 0U;
        __Vdly__can_fd_tx__DOT__grp = 0U;
    }
    vlSelfRef.can_fd_tx__DOT__wr_len = __Vdly__can_fd_tx__DOT__wr_len;
    vlSelfRef.can_fd_tx__DOT__run_cnt = __Vdly__can_fd_tx__DOT__run_cnt;
    vlSelfRef.can_fd_tx__DOT__crc_reg = __Vdly__can_fd_tx__DOT__crc_reg;
    vlSelfRef.can_fd_tx__DOT__run_bit = __Vdly__can_fd_tx__DOT__run_bit;
    vlSelfRef.can_fd_tx__DOT__sc_idx = __Vdly__can_fd_tx__DOT__sc_idx;
    vlSelfRef.can_fd_tx__DOT__crc_idx = __Vdly__can_fd_tx__DOT__crc_idx;
    vlSelfRef.can_fd_tx__DOT__grp = __Vdly__can_fd_tx__DOT__grp;
    vlSelfRef.can_fd_tx__DOT__crc_final = __Vdly__can_fd_tx__DOT__crc_final;
    vlSelfRef.can_fd_tx__DOT__rd_idx = __Vdly__can_fd_tx__DOT__rd_idx;
    vlSelfRef.can_fd_tx__DOT__tail_idx = __Vdly__can_fd_tx__DOT__tail_idx;
    vlSelfRef.can_fd_tx__DOT__dyn = __Vdly__can_fd_tx__DOT__dyn;
    vlSelfRef.can_fd_tx__DOT__state = __Vdly__can_fd_tx__DOT__state;
    vlSelfRef.can_fd_tx__DOT__raw_idx = __Vdly__can_fd_tx__DOT__raw_idx;
    if (__VdlySet__can_fd_tx__DOT__frame_buf__v0) {
        vlSelfRef.can_fd_tx__DOT__frame_buf[__VdlyDim0__can_fd_tx__DOT__frame_buf__v0] 
            = __VdlyVal__can_fd_tx__DOT__frame_buf__v0;
    }
    if (__VdlySet__can_fd_tx__DOT__frame_buf__v1) {
        vlSelfRef.can_fd_tx__DOT__frame_buf[__VdlyDim0__can_fd_tx__DOT__frame_buf__v1] 
            = __VdlyVal__can_fd_tx__DOT__frame_buf__v1;
    }
    if (__VdlySet__can_fd_tx__DOT__frame_buf__v2) {
        vlSelfRef.can_fd_tx__DOT__frame_buf[__VdlyDim0__can_fd_tx__DOT__frame_buf__v2] 
            = __VdlyVal__can_fd_tx__DOT__frame_buf__v2;
    }
    if (__VdlySet__can_fd_tx__DOT__frame_buf__v3) {
        vlSelfRef.can_fd_tx__DOT__frame_buf[__VdlyDim0__can_fd_tx__DOT__frame_buf__v3] 
            = __VdlyVal__can_fd_tx__DOT__frame_buf__v3;
    }
    if (__VdlySet__can_fd_tx__DOT__frame_buf__v4) {
        vlSelfRef.can_fd_tx__DOT__frame_buf[__VdlyDim0__can_fd_tx__DOT__frame_buf__v4] 
            = __VdlyVal__can_fd_tx__DOT__frame_buf__v4;
    }
    if (__VdlySet__can_fd_tx__DOT__frame_buf__v5) {
        vlSelfRef.can_fd_tx__DOT__frame_buf[__VdlyDim0__can_fd_tx__DOT__frame_buf__v5] 
            = __VdlyVal__can_fd_tx__DOT__frame_buf__v5;
    }
    if (__VdlySet__can_fd_tx__DOT__frame_buf__v6) {
        vlSelfRef.can_fd_tx__DOT__frame_buf[__VdlyDim0__can_fd_tx__DOT__frame_buf__v6] = 1U;
    }
    vlSelfRef.tx_bit_valid = vlSelfRef.can_fd_tx__DOT__tx_bit_valid;
    vlSelfRef.tx_bit = vlSelfRef.can_fd_tx__DOT__tx_bit;
    vlSelfRef.can_fd_tx__DOT__gray = (7U & ((IData)(vlSelfRef.can_fd_tx__DOT__dyn) 
                                            ^ VL_SHIFTR_III(3,3,32, (IData)(vlSelfRef.can_fd_tx__DOT__dyn), 1U)));
    vlSelfRef.can_fd_tx__DOT__tx_done = (8U == (IData)(vlSelfRef.can_fd_tx__DOT__state));
    vlSelfRef.can_fd_tx__DOT__tx_busy = ((0U != (IData)(vlSelfRef.can_fd_tx__DOT__state)) 
                                         & (8U != (IData)(vlSelfRef.can_fd_tx__DOT__state)));
    vlSelfRef.can_fd_tx__DOT__di = (0x1ffU & ((IData)(vlSelfRef.can_fd_tx__DOT__raw_idx) 
                                              - (IData)(0x16U)));
    __Vtableidx1 = vlSelfRef.can_fd_tx__DOT__dlc_reg;
    vlSelfRef.can_fd_tx__DOT__data_bytes = Vtop__ConstPool__TABLE_h2a89ce04_0
        [__Vtableidx1];
    vlSelfRef.can_fd_tx__DOT__is_crc21 = (0xdU <= (IData)(vlSelfRef.can_fd_tx__DOT__dlc_reg));
    vlSelfRef.can_fd_tx__DOT__sc_field = (((IData)(vlSelfRef.can_fd_tx__DOT__gray) 
                                           << 1U) | 
                                          (1U & VL_REDXOR_4(vlSelfRef.can_fd_tx__DOT__gray)));
    vlSelfRef.tx_done = vlSelfRef.can_fd_tx__DOT__tx_done;
    vlSelfRef.tx_busy = vlSelfRef.can_fd_tx__DOT__tx_busy;
    vlSelfRef.can_fd_tx__DOT__raw_bit = ((0U != (IData)(vlSelfRef.can_fd_tx__DOT__raw_idx)) 
                                         && (1U & (
                                                   (0xbU 
                                                    >= (IData)(vlSelfRef.can_fd_tx__DOT__raw_idx))
                                                    ? 
                                                   ((0xaU 
                                                     >= 
                                                     (0xfU 
                                                      & ((IData)(0xbU) 
                                                         - (IData)(vlSelfRef.can_fd_tx__DOT__raw_idx)))) 
                                                    && (1U 
                                                        & ((IData)(vlSelfRef.can_fd_tx__DOT__id_reg) 
                                                           >> 
                                                           (0xfU 
                                                            & ((IData)(0xbU) 
                                                               - (IData)(vlSelfRef.can_fd_tx__DOT__raw_idx))))))
                                                    : 
                                                   ((0x11U 
                                                     >= (IData)(vlSelfRef.can_fd_tx__DOT__raw_idx))
                                                     ? 
                                                    ((0xcU 
                                                      != (IData)(vlSelfRef.can_fd_tx__DOT__raw_idx)) 
                                                     && ((0xdU 
                                                          != (IData)(vlSelfRef.can_fd_tx__DOT__raw_idx)) 
                                                         && ((0xeU 
                                                              == (IData)(vlSelfRef.can_fd_tx__DOT__raw_idx)) 
                                                             || ((0xfU 
                                                                  != (IData)(vlSelfRef.can_fd_tx__DOT__raw_idx)) 
                                                                 && ((0x10U 
                                                                      == (IData)(vlSelfRef.can_fd_tx__DOT__raw_idx)) 
                                                                     && (IData)(vlSelfRef.can_fd_tx__DOT__brs_reg))))))
                                                     : 
                                                    ((0x15U 
                                                      >= (IData)(vlSelfRef.can_fd_tx__DOT__raw_idx))
                                                      ? 
                                                     ((0x12U 
                                                       == (IData)(vlSelfRef.can_fd_tx__DOT__raw_idx))
                                                       ? 
                                                      ((IData)(vlSelfRef.can_fd_tx__DOT__dlc_reg) 
                                                       >> 3U)
                                                       : 
                                                      ((0x13U 
                                                        == (IData)(vlSelfRef.can_fd_tx__DOT__raw_idx))
                                                        ? 
                                                       ((IData)(vlSelfRef.can_fd_tx__DOT__dlc_reg) 
                                                        >> 2U)
                                                        : 
                                                       ((0x14U 
                                                         == (IData)(vlSelfRef.can_fd_tx__DOT__raw_idx))
                                                         ? 
                                                        ((IData)(vlSelfRef.can_fd_tx__DOT__dlc_reg) 
                                                         >> 1U)
                                                         : 
                                                        ((0x15U 
                                                          == (IData)(vlSelfRef.can_fd_tx__DOT__raw_idx)) 
                                                         && (1U 
                                                             & (IData)(vlSelfRef.can_fd_tx__DOT__dlc_reg))))))
                                                      : 
                                                     (vlSelfRef.can_fd_tx__DOT__data_reg[
                                                      (0xfU 
                                                       & (((IData)(0x1ffU) 
                                                           - (IData)(vlSelfRef.can_fd_tx__DOT__di)) 
                                                          >> 5U))] 
                                                      >> 
                                                      (0x1fU 
                                                       & ((IData)(0x1ffU) 
                                                          - (IData)(vlSelfRef.can_fd_tx__DOT__di)))))))));
    vlSelfRef.can_fd_tx__DOT__raw_total = (0x3ffU & 
                                           ((IData)(0x16U) 
                                            + VL_SHIFTL_III(10,10,32, (IData)(vlSelfRef.can_fd_tx__DOT__data_bytes), 3U)));
    if (vlSelfRef.can_fd_tx__DOT__is_crc21) {
        vlSelfRef.can_fd_tx__DOT__cmask = 0x1fffffU;
        vlSelfRef.can_fd_tx__DOT__poly = 0x102899U;
        vlSelfRef.can_fd_tx__DOT__cw = 0x15U;
    } else {
        vlSelfRef.can_fd_tx__DOT__cmask = 0x1ffffU;
        vlSelfRef.can_fd_tx__DOT__poly = 0x1685bU;
        vlSelfRef.can_fd_tx__DOT__cw = 0x11U;
    }
}

void Vtop___024root___eval_triggers__act(Vtop___024root* vlSelf);

bool Vtop___024root___eval_phase__act(Vtop___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtop___024root___eval_phase__act\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Init
    VlTriggerVec<2> __VpreTriggered;
    CData/*0:0*/ __VactExecute;
    // Body
    Vtop___024root___eval_triggers__act(vlSelf);
    __VactExecute = vlSelfRef.__VactTriggered.any();
    if (__VactExecute) {
        __VpreTriggered.andNot(vlSelfRef.__VactTriggered, vlSelfRef.__VnbaTriggered);
        vlSelfRef.__VnbaTriggered.thisOr(vlSelfRef.__VactTriggered);
        Vtop___024root___eval_act(vlSelf);
    }
    return (__VactExecute);
}

bool Vtop___024root___eval_phase__nba(Vtop___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtop___024root___eval_phase__nba\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Init
    CData/*0:0*/ __VnbaExecute;
    // Body
    __VnbaExecute = vlSelfRef.__VnbaTriggered.any();
    if (__VnbaExecute) {
        Vtop___024root___eval_nba(vlSelf);
        vlSelfRef.__VnbaTriggered.clear();
    }
    return (__VnbaExecute);
}

#ifdef VL_DEBUG
VL_ATTR_COLD void Vtop___024root___dump_triggers__ico(Vtop___024root* vlSelf);
#endif  // VL_DEBUG
#ifdef VL_DEBUG
VL_ATTR_COLD void Vtop___024root___dump_triggers__nba(Vtop___024root* vlSelf);
#endif  // VL_DEBUG
#ifdef VL_DEBUG
VL_ATTR_COLD void Vtop___024root___dump_triggers__act(Vtop___024root* vlSelf);
#endif  // VL_DEBUG

void Vtop___024root___eval(Vtop___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtop___024root___eval\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Init
    IData/*31:0*/ __VicoIterCount;
    CData/*0:0*/ __VicoContinue;
    IData/*31:0*/ __VnbaIterCount;
    CData/*0:0*/ __VnbaContinue;
    // Body
    __VicoIterCount = 0U;
    vlSelfRef.__VicoFirstIteration = 1U;
    __VicoContinue = 1U;
    while (__VicoContinue) {
        if (VL_UNLIKELY(((0x64U < __VicoIterCount)))) {
#ifdef VL_DEBUG
            Vtop___024root___dump_triggers__ico(vlSelf);
#endif
            VL_FATAL_MT("/root/can-fd-core/rtl/can_fd_tx.sv", 2, "", "Input combinational region did not converge.");
        }
        __VicoIterCount = ((IData)(1U) + __VicoIterCount);
        __VicoContinue = 0U;
        if (Vtop___024root___eval_phase__ico(vlSelf)) {
            __VicoContinue = 1U;
        }
        vlSelfRef.__VicoFirstIteration = 0U;
    }
    __VnbaIterCount = 0U;
    __VnbaContinue = 1U;
    while (__VnbaContinue) {
        if (VL_UNLIKELY(((0x64U < __VnbaIterCount)))) {
#ifdef VL_DEBUG
            Vtop___024root___dump_triggers__nba(vlSelf);
#endif
            VL_FATAL_MT("/root/can-fd-core/rtl/can_fd_tx.sv", 2, "", "NBA region did not converge.");
        }
        __VnbaIterCount = ((IData)(1U) + __VnbaIterCount);
        __VnbaContinue = 0U;
        vlSelfRef.__VactIterCount = 0U;
        vlSelfRef.__VactContinue = 1U;
        while (vlSelfRef.__VactContinue) {
            if (VL_UNLIKELY(((0x64U < vlSelfRef.__VactIterCount)))) {
#ifdef VL_DEBUG
                Vtop___024root___dump_triggers__act(vlSelf);
#endif
                VL_FATAL_MT("/root/can-fd-core/rtl/can_fd_tx.sv", 2, "", "Active region did not converge.");
            }
            vlSelfRef.__VactIterCount = ((IData)(1U) 
                                         + vlSelfRef.__VactIterCount);
            vlSelfRef.__VactContinue = 0U;
            if (Vtop___024root___eval_phase__act(vlSelf)) {
                vlSelfRef.__VactContinue = 1U;
            }
        }
        if (Vtop___024root___eval_phase__nba(vlSelf)) {
            __VnbaContinue = 1U;
        }
    }
}

#ifdef VL_DEBUG
void Vtop___024root___eval_debug_assertions(Vtop___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtop___024root___eval_debug_assertions\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if (VL_UNLIKELY(((vlSelfRef.clk & 0xfeU)))) {
        Verilated::overWidthError("clk");}
    if (VL_UNLIKELY(((vlSelfRef.rst_n & 0xfeU)))) {
        Verilated::overWidthError("rst_n");}
    if (VL_UNLIKELY(((vlSelfRef.tx_start & 0xfeU)))) {
        Verilated::overWidthError("tx_start");}
    if (VL_UNLIKELY(((vlSelfRef.tx_id & 0xf800U)))) {
        Verilated::overWidthError("tx_id");}
    if (VL_UNLIKELY(((vlSelfRef.tx_dlc & 0xf0U)))) {
        Verilated::overWidthError("tx_dlc");}
    if (VL_UNLIKELY(((vlSelfRef.tx_brs & 0xfeU)))) {
        Verilated::overWidthError("tx_brs");}
}
#endif  // VL_DEBUG
