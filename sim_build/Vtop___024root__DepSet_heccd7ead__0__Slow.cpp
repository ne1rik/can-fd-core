// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design implementation internals
// See Vtop.h for the primary calling header

#include "Vtop__pch.h"
#include "Vtop___024root.h"

VL_ATTR_COLD void Vtop___024root___eval_static(Vtop___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtop___024root___eval_static\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.__Vtrigprevexpr___TOP__clk__0 = vlSelfRef.clk;
    vlSelfRef.__Vtrigprevexpr___TOP__rst_n__0 = vlSelfRef.rst_n;
}

VL_ATTR_COLD void Vtop___024root___eval_initial(Vtop___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtop___024root___eval_initial\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
}

VL_ATTR_COLD void Vtop___024root___eval_final(Vtop___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtop___024root___eval_final\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
}

#ifdef VL_DEBUG
VL_ATTR_COLD void Vtop___024root___dump_triggers__stl(Vtop___024root* vlSelf);
#endif  // VL_DEBUG
VL_ATTR_COLD bool Vtop___024root___eval_phase__stl(Vtop___024root* vlSelf);

VL_ATTR_COLD void Vtop___024root___eval_settle(Vtop___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtop___024root___eval_settle\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Init
    IData/*31:0*/ __VstlIterCount;
    CData/*0:0*/ __VstlContinue;
    // Body
    __VstlIterCount = 0U;
    vlSelfRef.__VstlFirstIteration = 1U;
    __VstlContinue = 1U;
    while (__VstlContinue) {
        if (VL_UNLIKELY(((0x64U < __VstlIterCount)))) {
#ifdef VL_DEBUG
            Vtop___024root___dump_triggers__stl(vlSelf);
#endif
            VL_FATAL_MT("/root/can-fd-core/rtl/can_fd_tx.sv", 2, "", "Settle region did not converge.");
        }
        __VstlIterCount = ((IData)(1U) + __VstlIterCount);
        __VstlContinue = 0U;
        if (Vtop___024root___eval_phase__stl(vlSelf)) {
            __VstlContinue = 1U;
        }
        vlSelfRef.__VstlFirstIteration = 0U;
    }
}

#ifdef VL_DEBUG
VL_ATTR_COLD void Vtop___024root___dump_triggers__stl(Vtop___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtop___024root___dump_triggers__stl\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if ((1U & (~ vlSelfRef.__VstlTriggered.any()))) {
        VL_DBG_MSGF("         No triggers active\n");
    }
    if ((1ULL & vlSelfRef.__VstlTriggered.word(0U))) {
        VL_DBG_MSGF("         'stl' region trigger index 0 is active: Internal 'stl' trigger - first iteration\n");
    }
}
#endif  // VL_DEBUG

void Vtop___024root___ico_sequent__TOP__0(Vtop___024root* vlSelf);

VL_ATTR_COLD void Vtop___024root___eval_stl(Vtop___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtop___024root___eval_stl\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if ((1ULL & vlSelfRef.__VstlTriggered.word(0U))) {
        Vtop___024root___ico_sequent__TOP__0(vlSelf);
    }
}

VL_ATTR_COLD void Vtop___024root___eval_triggers__stl(Vtop___024root* vlSelf);

VL_ATTR_COLD bool Vtop___024root___eval_phase__stl(Vtop___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtop___024root___eval_phase__stl\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Init
    CData/*0:0*/ __VstlExecute;
    // Body
    Vtop___024root___eval_triggers__stl(vlSelf);
    __VstlExecute = vlSelfRef.__VstlTriggered.any();
    if (__VstlExecute) {
        Vtop___024root___eval_stl(vlSelf);
    }
    return (__VstlExecute);
}

#ifdef VL_DEBUG
VL_ATTR_COLD void Vtop___024root___dump_triggers__ico(Vtop___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtop___024root___dump_triggers__ico\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if ((1U & (~ vlSelfRef.__VicoTriggered.any()))) {
        VL_DBG_MSGF("         No triggers active\n");
    }
    if ((1ULL & vlSelfRef.__VicoTriggered.word(0U))) {
        VL_DBG_MSGF("         'ico' region trigger index 0 is active: Internal 'ico' trigger - first iteration\n");
    }
}
#endif  // VL_DEBUG

#ifdef VL_DEBUG
VL_ATTR_COLD void Vtop___024root___dump_triggers__act(Vtop___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtop___024root___dump_triggers__act\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if ((1U & (~ vlSelfRef.__VactTriggered.any()))) {
        VL_DBG_MSGF("         No triggers active\n");
    }
    if ((1ULL & vlSelfRef.__VactTriggered.word(0U))) {
        VL_DBG_MSGF("         'act' region trigger index 0 is active: @(posedge clk)\n");
    }
    if ((2ULL & vlSelfRef.__VactTriggered.word(0U))) {
        VL_DBG_MSGF("         'act' region trigger index 1 is active: @(negedge rst_n)\n");
    }
}
#endif  // VL_DEBUG

#ifdef VL_DEBUG
VL_ATTR_COLD void Vtop___024root___dump_triggers__nba(Vtop___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtop___024root___dump_triggers__nba\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if ((1U & (~ vlSelfRef.__VnbaTriggered.any()))) {
        VL_DBG_MSGF("         No triggers active\n");
    }
    if ((1ULL & vlSelfRef.__VnbaTriggered.word(0U))) {
        VL_DBG_MSGF("         'nba' region trigger index 0 is active: @(posedge clk)\n");
    }
    if ((2ULL & vlSelfRef.__VnbaTriggered.word(0U))) {
        VL_DBG_MSGF("         'nba' region trigger index 1 is active: @(negedge rst_n)\n");
    }
}
#endif  // VL_DEBUG

VL_ATTR_COLD void Vtop___024root___ctor_var_reset(Vtop___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtop___024root___ctor_var_reset\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelf->clk = VL_RAND_RESET_I(1);
    vlSelf->rst_n = VL_RAND_RESET_I(1);
    vlSelf->tx_start = VL_RAND_RESET_I(1);
    vlSelf->tx_id = VL_RAND_RESET_I(11);
    vlSelf->tx_dlc = VL_RAND_RESET_I(4);
    VL_RAND_RESET_W(512, vlSelf->tx_data);
    vlSelf->tx_brs = VL_RAND_RESET_I(1);
    vlSelf->tx_bit = VL_RAND_RESET_I(1);
    vlSelf->tx_bit_valid = VL_RAND_RESET_I(1);
    vlSelf->tx_done = VL_RAND_RESET_I(1);
    vlSelf->tx_busy = VL_RAND_RESET_I(1);
    vlSelf->can_fd_tx__DOT__clk = VL_RAND_RESET_I(1);
    vlSelf->can_fd_tx__DOT__rst_n = VL_RAND_RESET_I(1);
    vlSelf->can_fd_tx__DOT__tx_start = VL_RAND_RESET_I(1);
    vlSelf->can_fd_tx__DOT__tx_id = VL_RAND_RESET_I(11);
    vlSelf->can_fd_tx__DOT__tx_dlc = VL_RAND_RESET_I(4);
    VL_RAND_RESET_W(512, vlSelf->can_fd_tx__DOT__tx_data);
    vlSelf->can_fd_tx__DOT__tx_brs = VL_RAND_RESET_I(1);
    vlSelf->can_fd_tx__DOT__tx_bit = VL_RAND_RESET_I(1);
    vlSelf->can_fd_tx__DOT__tx_bit_valid = VL_RAND_RESET_I(1);
    vlSelf->can_fd_tx__DOT__tx_done = VL_RAND_RESET_I(1);
    vlSelf->can_fd_tx__DOT__tx_busy = VL_RAND_RESET_I(1);
    vlSelf->can_fd_tx__DOT__state = VL_RAND_RESET_I(4);
    vlSelf->can_fd_tx__DOT__id_reg = VL_RAND_RESET_I(11);
    vlSelf->can_fd_tx__DOT__dlc_reg = VL_RAND_RESET_I(4);
    VL_RAND_RESET_W(512, vlSelf->can_fd_tx__DOT__data_reg);
    vlSelf->can_fd_tx__DOT__brs_reg = VL_RAND_RESET_I(1);
    for (int __Vi0 = 0; __Vi0 < 1024; ++__Vi0) {
        vlSelf->can_fd_tx__DOT__frame_buf[__Vi0] = VL_RAND_RESET_I(1);
    }
    vlSelf->can_fd_tx__DOT__wr_len = VL_RAND_RESET_I(10);
    vlSelf->can_fd_tx__DOT__rd_idx = VL_RAND_RESET_I(10);
    vlSelf->can_fd_tx__DOT__raw_idx = VL_RAND_RESET_I(10);
    vlSelf->can_fd_tx__DOT__run_cnt = VL_RAND_RESET_I(3);
    vlSelf->can_fd_tx__DOT__run_bit = VL_RAND_RESET_I(1);
    vlSelf->can_fd_tx__DOT__dyn = VL_RAND_RESET_I(3);
    vlSelf->can_fd_tx__DOT__crc_reg = VL_RAND_RESET_I(21);
    vlSelf->can_fd_tx__DOT__crc_final = VL_RAND_RESET_I(21);
    vlSelf->can_fd_tx__DOT__sc_idx = VL_RAND_RESET_I(2);
    vlSelf->can_fd_tx__DOT__crc_idx = VL_RAND_RESET_I(5);
    vlSelf->can_fd_tx__DOT__grp = VL_RAND_RESET_I(3);
    vlSelf->can_fd_tx__DOT__tail_idx = VL_RAND_RESET_I(4);
    vlSelf->can_fd_tx__DOT__is_crc21 = VL_RAND_RESET_I(1);
    vlSelf->can_fd_tx__DOT__cw = VL_RAND_RESET_I(5);
    vlSelf->can_fd_tx__DOT__poly = VL_RAND_RESET_I(21);
    vlSelf->can_fd_tx__DOT__cmask = VL_RAND_RESET_I(21);
    vlSelf->can_fd_tx__DOT__crc_step__Vstatic__m = VL_RAND_RESET_I(1);
    vlSelf->can_fd_tx__DOT__crc_step__Vstatic__sh = VL_RAND_RESET_I(21);
    vlSelf->can_fd_tx__DOT__data_bytes = VL_RAND_RESET_I(7);
    vlSelf->can_fd_tx__DOT__raw_total = VL_RAND_RESET_I(10);
    vlSelf->can_fd_tx__DOT__gray = VL_RAND_RESET_I(3);
    vlSelf->can_fd_tx__DOT__sc_field = VL_RAND_RESET_I(4);
    vlSelf->can_fd_tx__DOT__raw_bit = VL_RAND_RESET_I(1);
    vlSelf->can_fd_tx__DOT__di = VL_RAND_RESET_I(9);
    vlSelf->__Vtrigprevexpr___TOP__clk__0 = VL_RAND_RESET_I(1);
    vlSelf->__Vtrigprevexpr___TOP__rst_n__0 = VL_RAND_RESET_I(1);
}
