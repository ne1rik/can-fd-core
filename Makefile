TOPLEVEL_LANG = verilog
VERILOG_SOURCES = $(PWD)/rtl/can_fd_tx.sv
TOPLEVEL = can_fd_tx
COCOTB_TEST_MODULES = tb.test_can_fd_tx
SIM ?= verilator
export PYTHONPATH := $(PWD)/tb:$(PYTHONPATH)
include $(shell cocotb-config --makefiles)/Makefile.sim
