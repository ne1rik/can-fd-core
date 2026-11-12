TOPLEVEL_LANG = verilog
VERILOG_SOURCES = $(PWD)/rtl/can_fd_ctrl.sv
TOPLEVEL = can_fd_ctrl
COCOTB_TEST_MODULES = tb.test_can_fd
SIM ?= verilator

# Добавляем tb в PYTHONPATH, чтобы тесты могли импортировать can_fd_reference
export PYTHONPATH := $(PWD)/tb:$(PYTHONPATH)

include $(shell cocotb-config --makefiles)/Makefile.sim
