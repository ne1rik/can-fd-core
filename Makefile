TOPLEVEL_LANG = verilog
VERILOG_SOURCES = $(PWD)/rtl/bit_stuffer.sv $(PWD)/rtl/crc17_canfd.sv
TOPLEVEL = crc17_canfd
COCOTB_TEST_MODULES = tb.test_crc17
SIM ?= verilator

export PYTHONPATH := $(PWD)/tb:$(PYTHONPATH)

include $(shell cocotb-config --makefiles)/Makefile.sim
