# Main regression: CAN FD TX (DUT #1) + Integration tests
SIM ?= verilator
TOPLEVEL_LANG = verilog
VERILOG_SOURCES = $(PWD)/rtl/can_fd_tx.sv
TOPLEVEL = can_fd_tx
# Только cocotb-тесты (с @cocotb.test())
COCOTB_TEST_MODULES = tests.test_canfd_tx_integration

export PYTHONPATH := $(PWD)/tb:$(PWD):$(PYTHONPATH)

include $(shell cocotb-config --makefiles)/Makefile.sim
