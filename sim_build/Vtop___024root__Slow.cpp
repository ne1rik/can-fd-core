// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design implementation internals
// See Vtop.h for the primary calling header

#include "Vtop__pch.h"
#include "Vtop__Syms.h"
#include "Vtop___024root.h"

// Parameter definitions for Vtop___024root
constexpr IData/*31:0*/ Vtop___024root::can_fd_tx__DOT__IDLE;
constexpr IData/*31:0*/ Vtop___024root::can_fd_tx__DOT__F_RAW;
constexpr IData/*31:0*/ Vtop___024root::can_fd_tx__DOT__F_STUFF;
constexpr IData/*31:0*/ Vtop___024root::can_fd_tx__DOT__F_FSB1;
constexpr IData/*31:0*/ Vtop___024root::can_fd_tx__DOT__F_SC;
constexpr IData/*31:0*/ Vtop___024root::can_fd_tx__DOT__F_CRC;
constexpr IData/*31:0*/ Vtop___024root::can_fd_tx__DOT__F_TAIL;
constexpr IData/*31:0*/ Vtop___024root::can_fd_tx__DOT__F_SHIFT;
constexpr IData/*31:0*/ Vtop___024root::can_fd_tx__DOT__DONE;


void Vtop___024root___ctor_var_reset(Vtop___024root* vlSelf);

Vtop___024root::Vtop___024root(Vtop__Syms* symsp, const char* v__name)
    : VerilatedModule{v__name}
    , vlSymsp{symsp}
 {
    // Reset structure values
    Vtop___024root___ctor_var_reset(this);
}

void Vtop___024root::__Vconfigure(bool first) {
    (void)first;  // Prevent unused variable warning
}

Vtop___024root::~Vtop___024root() {
}
