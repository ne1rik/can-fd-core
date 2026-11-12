TOPLEVEL_LANG = verilog
VERILOG_SOURCES = $(PWD)/rtl/dummy.sv
TOPLEVEL = dummy
COCOTB_TEST_MODULES = tb.test_dummy
SIM ?= verilator

include $(shell cocotb-config --makefiles)/Makefile.sim
