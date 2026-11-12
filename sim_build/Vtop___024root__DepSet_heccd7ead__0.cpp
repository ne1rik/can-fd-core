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

VL_INLINE_OPT void Vtop___024root___ico_sequent__TOP__0(Vtop___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtop___024root___ico_sequent__TOP__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.bit_stuffer__DOT__clk = vlSelfRef.clk;
    vlSelfRef.bit_stuffer__DOT__rst_n = vlSelfRef.rst_n;
    vlSelfRef.bit_stuffer__DOT__data_in = vlSelfRef.data_in;
    vlSelfRef.bit_stuffer__DOT__data_in_valid = vlSelfRef.data_in_valid;
    vlSelfRef.data_out = vlSelfRef.bit_stuffer__DOT__data_out;
    vlSelfRef.data_out_valid = vlSelfRef.bit_stuffer__DOT__data_out_valid;
    vlSelfRef.stuff_count = vlSelfRef.bit_stuffer__DOT__stuff_count;
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
    CData/*2:0*/ __Vdly__bit_stuffer__DOT__consecutive_count;
    __Vdly__bit_stuffer__DOT__consecutive_count = 0;
    CData/*0:0*/ __Vdly__bit_stuffer__DOT__last_bit;
    __Vdly__bit_stuffer__DOT__last_bit = 0;
    // Body
    __Vdly__bit_stuffer__DOT__consecutive_count = vlSelfRef.bit_stuffer__DOT__consecutive_count;
    __Vdly__bit_stuffer__DOT__last_bit = vlSelfRef.bit_stuffer__DOT__last_bit;
    if (vlSelfRef.rst_n) {
        if (vlSelfRef.bit_stuffer__DOT__need_stuff_bit) {
            vlSelfRef.bit_stuffer__DOT__stuff_count 
                = (0xffU & ((IData)(1U) + (IData)(vlSelfRef.bit_stuffer__DOT__stuff_count)));
            vlSelfRef.bit_stuffer__DOT__data_out = 
                (1U & (~ (IData)(vlSelfRef.bit_stuffer__DOT__last_bit)));
            vlSelfRef.bit_stuffer__DOT__data_out_valid = 1U;
            __Vdly__bit_stuffer__DOT__consecutive_count = 1U;
            vlSelfRef.bit_stuffer__DOT__need_stuff_bit = 0U;
            __Vdly__bit_stuffer__DOT__last_bit = (1U 
                                                  & (~ (IData)(vlSelfRef.bit_stuffer__DOT__last_bit)));
        } else if (vlSelfRef.data_in_valid) {
            vlSelfRef.bit_stuffer__DOT__data_out = vlSelfRef.data_in;
            vlSelfRef.bit_stuffer__DOT__data_out_valid = 1U;
            if (vlSelfRef.bit_stuffer__DOT__first_bit) {
                __Vdly__bit_stuffer__DOT__last_bit 
                    = vlSelfRef.data_in;
                __Vdly__bit_stuffer__DOT__consecutive_count = 1U;
                vlSelfRef.bit_stuffer__DOT__first_bit = 0U;
            } else if (((IData)(vlSelfRef.data_in) 
                        == (IData)(vlSelfRef.bit_stuffer__DOT__last_bit))) {
                if ((4U == (IData)(vlSelfRef.bit_stuffer__DOT__consecutive_count))) {
                    vlSelfRef.bit_stuffer__DOT__need_stuff_bit = 1U;
                }
                __Vdly__bit_stuffer__DOT__consecutive_count 
                    = (7U & ((IData)(1U) + (IData)(vlSelfRef.bit_stuffer__DOT__consecutive_count)));
            } else {
                __Vdly__bit_stuffer__DOT__last_bit 
                    = vlSelfRef.data_in;
                __Vdly__bit_stuffer__DOT__consecutive_count = 1U;
            }
        } else {
            vlSelfRef.bit_stuffer__DOT__data_out_valid = 0U;
        }
    } else {
        vlSelfRef.bit_stuffer__DOT__stuff_count = 0U;
        __Vdly__bit_stuffer__DOT__last_bit = 0U;
        vlSelfRef.bit_stuffer__DOT__data_out = 1U;
        vlSelfRef.bit_stuffer__DOT__data_out_valid = 0U;
        __Vdly__bit_stuffer__DOT__consecutive_count = 0U;
        vlSelfRef.bit_stuffer__DOT__need_stuff_bit = 0U;
        vlSelfRef.bit_stuffer__DOT__first_bit = 1U;
    }
    vlSelfRef.bit_stuffer__DOT__consecutive_count = __Vdly__bit_stuffer__DOT__consecutive_count;
    vlSelfRef.bit_stuffer__DOT__last_bit = __Vdly__bit_stuffer__DOT__last_bit;
    vlSelfRef.stuff_count = vlSelfRef.bit_stuffer__DOT__stuff_count;
    vlSelfRef.data_out = vlSelfRef.bit_stuffer__DOT__data_out;
    vlSelfRef.data_out_valid = vlSelfRef.bit_stuffer__DOT__data_out_valid;
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
            VL_FATAL_MT("/root/can-fd-core/rtl/bit_stuffer.sv", 3, "", "Input combinational region did not converge.");
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
            VL_FATAL_MT("/root/can-fd-core/rtl/bit_stuffer.sv", 3, "", "NBA region did not converge.");
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
                VL_FATAL_MT("/root/can-fd-core/rtl/bit_stuffer.sv", 3, "", "Active region did not converge.");
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
    if (VL_UNLIKELY(((vlSelfRef.data_in & 0xfeU)))) {
        Verilated::overWidthError("data_in");}
    if (VL_UNLIKELY(((vlSelfRef.data_in_valid & 0xfeU)))) {
        Verilated::overWidthError("data_in_valid");}
}
#endif  // VL_DEBUG
