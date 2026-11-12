TOPLEVEL_LANG = verilog
VERILOG_SOURCES = $(PWD)/rtl/can_fd_ctrl.sv $(PWD)/rtl/bit_stuffer.sv
TOPLEVEL = bit_stuffer
COCOTB_TEST_MODULES = tb.test_bit_stuffer
SIM ?= verilator

export PYTHONPATH := $(PWD)/tb:$(PYTHONPATH)

include $(shell cocotb-config --makefiles)/Makefile.sim
