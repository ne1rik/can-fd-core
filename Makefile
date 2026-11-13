# Main regression: CAN FD TX core (DUT #1) + monitor integration.
SIM ?= verilator
TOPLEVEL_LANG = verilog
VERILOG_SOURCES = $(PWD)/rtl/can_fd_tx.sv
TOPLEVEL = can_fd_tx
COCOTB_TEST_MODULES = tb.test_can_fd_tx,tests.test_canfd_tx_integration
SIM_BUILD = $(PWD)/sim_build_tx

export PYTHONPATH := $(PWD)/tb:$(PWD):$(PYTHONPATH)

include $(shell cocotb-config --makefiles)/Makefile.sim
