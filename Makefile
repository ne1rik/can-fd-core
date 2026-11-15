# Main regression: CAN FD TX core (DUT #1) + monitor integration.
SIM ?= verilator
TOPLEVEL_LANG = verilog
VERILOG_SOURCES = $(PWD)/rtl/can_fd_tx.sv $(PWD)/rtl/can_bit_timing.sv
TOPLEVEL = can_fd_tx
COCOTB_TEST_MODULES = tb.test_can_fd_tx,tests.test_canfd_tx_integration,tests.test_tx_sweep
SIM_BUILD = $(PWD)/sim_build_tx

export PYTHONPATH := $(PWD)/tb:$(PWD):$(PYTHONPATH)

include $(shell cocotb-config --makefiles)/Makefile.sim
