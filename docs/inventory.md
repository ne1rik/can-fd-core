# Repository inventory

Generated: 2026-11-13 11:04 UTC

## Tracked files
```
.github/workflows/ci.yml
.gitignore
Makefile
README.md
TRACKING.md
debug_bit_stuffer.py
docs/bit_timings.md
results.xml
rtl/bit_stuffer.sv
rtl/can_fd_ctrl.sv
rtl/can_fd_tx.sv
rtl/crc17_canfd.sv
rtl/crc_canfd.sv
sim_build/Vtop
sim_build/Vtop.cpp
sim_build/Vtop.h
sim_build/Vtop.mk
sim_build/Vtop__ALL.a
sim_build/Vtop__ALL.cpp
sim_build/Vtop__ALL.d
sim_build/Vtop__ALL.o
sim_build/Vtop__Dpi.cpp
sim_build/Vtop__Dpi.h
sim_build/Vtop__Syms.cpp
sim_build/Vtop__Syms.h
sim_build/Vtop___024root.h
sim_build/Vtop___024root__DepSet_h84412442__0.cpp
sim_build/Vtop___024root__DepSet_h84412442__0__Slow.cpp
sim_build/Vtop___024root__DepSet_heccd7ead__0.cpp
sim_build/Vtop___024root__DepSet_heccd7ead__0__Slow.cpp
sim_build/Vtop___024root__Slow.cpp
sim_build/Vtop__pch.h
sim_build/Vtop__ver.d
sim_build/Vtop__verFiles.dat
sim_build/Vtop_classes.mk
sim_build/verilated.d
sim_build/verilated.o
sim_build/verilated_dpi.d
sim_build/verilated_dpi.o
sim_build/verilated_threads.d
sim_build/verilated_threads.o
sim_build/verilated_vpi.d
sim_build/verilated_vpi.o
sim_build/verilator.d
sim_build/verilator.o
tb/__pycache__/test_dummy.cpython-312-pytest-9.2.0.pyc
tb/can_fd_reference.py
tb/test_bit_stuffer.py
tb/test_can_fd.py
tb/test_can_fd_tx.py
tb/test_crc17.py
tb/test_crc21.py
```

## RTL / testbench sizes
```
   59 rtl/bit_stuffer.sv
   50 rtl/can_fd_ctrl.sv
  147 rtl/can_fd_tx.sv
   35 rtl/crc17_canfd.sv
   43 rtl/crc_canfd.sv
   56 tb/can_fd_reference.py
   62 tb/test_bit_stuffer.py
   47 tb/test_can_fd.py
   54 tb/test_can_fd_tx.py
   73 tb/test_crc17.py
   38 tb/test_crc21.py
  664 total
```

## Git state
```
a27994a ci: fix Makefile targets and simplify GitHub Actions to use native Ubuntu 24.04 Verilator
1365616 ci: fix Makefile targets and simplify GitHub Actions to use native Ubuntu 24.04 Verilator
fe702b4 fix(tb): wait-for-idle handshake before tx_start; ISO CAN FD TX passes 6/6 incl back-to-back random
a92d4bb feat: CRC-21/CAN-FD generator for payload >= 20 bytes (1 test pass)
ba44f37 docs: update TRACKING.md with CRC-17 and bit stuffer completion
a176a79 feat: CRC-17/CAN-FD generator matching ISO 11898-1 (3 tests pass)
08a9fb0 feat: bit stuffer module with correct ISO 11898-1 logic (2 tests pass)
1e5e6d7 docs: update TRACKING.md with test infrastructure completion
b5f0c7e feat: working APB3 stub + Python reference model integration (2 tests pass)
f9cbcdf test: add initial cocotb testbench for APB3 stub and reference model
1876d01 feat: add initial CAN FD controller RTL stub with APB3 interface
4f94c72 docs: update TRACKING.md with reference model completion
9eb9bb1 feat: add verified ISO 11898-1 CAN FD reference model (CRC17/21, stuffing)
27b45df ci: add libfl-dev to fix Verilator build on Ubuntu
2187c3e docs: add CAN FD bit timing calculations for 80 MHz core
tags: v0.1 
```
