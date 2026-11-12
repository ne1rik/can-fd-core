TOPLEVEL_LANG = verilog
VERILOG_SOURCES = $(PWD)/rtl/crc_canfd.sv
TOPLEVEL = crc_canfd
COCOTB_TEST_MODULES = tb.test_crc21
SIM ?= verilator

# Передаём параметр CRC_WIDTH=21 в Verilator
EXTRA_ARGS = -GCRC_WIDTH=21

export PYTHONPATH := $(PWD)/tb:$(PYTHONPATH)

include $(shell cocotb-config --makefiles)/Makefile.sim
