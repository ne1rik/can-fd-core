#!/usr/bin/env bash
set -uo pipefail
cd "$(dirname "$0")/.." || exit 1
mkdir -p logs
SUM=logs/summary.txt
: > "$SUM"

run() {
  local name="$1"; shift
  printf '\n>>> %s\n' "$name"
  if "$@" > "logs/$name.log" 2>&1; then
    printf 'PASS  %s\n' "$name" | tee -a "$SUM"
  else
    printf 'FAIL  %s\n' "$name" | tee -a "$SUM"
    echo "--- tail logs/$name.log ---"; tail -30 "logs/$name.log"; echo "---------------------------"
  fi
}

run prep bash -c 'touch tests/__init__.py && python3 scripts/xval_ctu_extract_all.py'
run clean bash -c 'rm -rf sim_build_loopback sim_build_loopback_ext*_cls* sim_build_inject sim_build_inject_ext*_cls* sim_build_tx sim_build_aux sim_build_coverage sim_build_cov_inject'
run clean bash -c 'find . -type d \( -name __pycache__ -o -name .pytest_cache \) -prune -exec rm -rf {} +'  # guard: stale bytecode after mutation runs

run sanity bash -c '
set -e
verilator --version
grep -n "parameter int EXTENDED\|parameter int CLASSIC" rtl/can_fd_tx.sv rtl/can_fd_rx.sv rtl/can_fd_loopback.sv
grep -n "wire is_ext\|wire is_cls" rtl/can_fd_tx.sv rtl/can_fd_rx.sv
if grep -n "lint_off\|Wno-" rtl/*.sv; then echo "LINT SUPPRESSION FOUND"; exit 1; fi
if grep -n "1.d1" rtl/can_fd_tx.sv | grep -v "11.d1\|4.d1\|3.d1\|2.d1\|5.d1\|8.d1"; then echo "NARROW INCREMENT FOUND"; exit 1; fi
if [ -n "$(git diff -- tb/can_fd_reference.py)" ]; then echo "MODEL MODIFIED"; exit 1; fi
grep -n -A 30 "CRC_READ: begin" rtl/can_fd_rx.sv
'

run bnd_classic_base make -f Makefile.loopback EXTENDED=0 CLASSIC=1 TEST_MODULES=tests.test_crc_boundary
run bnd_classic_ext  make -f Makefile.loopback EXTENDED=1 CLASSIC=1 TEST_MODULES=tests.test_crc_boundary

run big_classic_base make -f Makefile.loopback EXTENDED=0 CLASSIC=1 TEST_MODULES=tests.test_big_sweep
run big_classic_ext  make -f Makefile.loopback EXTENDED=1 CLASSIC=1 TEST_MODULES=tests.test_big_sweep
run big_fd_base      make -f Makefile.loopback EXTENDED=0 CLASSIC=0 TEST_MODULES=tests.test_big_sweep
run big_fd_ext       make -f Makefile.loopback EXTENDED=1 CLASSIC=0 TEST_MODULES=tests.test_big_sweep

run ctu_classic_base make -f Makefile.loopback EXTENDED=0 CLASSIC=1 TEST_MODULES=tests.test_ctu_rtl
run ctu_classic_ext  make -f Makefile.loopback EXTENDED=1 CLASSIC=1 TEST_MODULES=tests.test_ctu_rtl
run ctu_fd_base      make -f Makefile.loopback EXTENDED=0 CLASSIC=0 TEST_MODULES=tests.test_ctu_rtl
run ctu_fd_ext       make -f Makefile.loopback EXTENDED=1 CLASSIC=0 TEST_MODULES=tests.test_ctu_rtl

# Bit-timing gates. These were missing from the runner, so the two-phase
# BRS work was not protected by regression. Each stage gets its own build
# directory because the build encodes the timing parameters.
run bt_units bash -c 'rm -rf sim_build_bt_units && make -f Makefile.bittiming SIM_BUILD=$PWD/sim_build_bt_units TEST_MODULES=tests.test_bit_timing'
run bt_phase_switch bash -c 'rm -rf sim_build_bt_ps && make -f Makefile.bittiming SIM_BUILD=$PWD/sim_build_bt_ps NBT_PRESCALER=1 NBT_TSEG1=12 NBT_TSEG2=4 DBT_PRESCALER=1 DBT_TSEG1=3 DBT_TSEG2=1 TEST_MODULES=tests.test_timing_phase_switch'
run rt_matrix_fbff bash -c 'rm -rf sim_build_rt_fbff && make -f Makefile.loopback SIM_BUILD=$PWD/sim_build_rt_fbff EXTENDED=0 CLASSIC=0 NBT_PRESCALER=1 NBT_TSEG1=12 NBT_TSEG2=4 DBT_PRESCALER=1 DBT_TSEG1=3 DBT_TSEG2=1 TEST_MODULES=tests.test_timing_matrix'
run rt_matrix_feff bash -c 'rm -rf sim_build_rt_feff && make -f Makefile.loopback SIM_BUILD=$PWD/sim_build_rt_feff EXTENDED=1 CLASSIC=0 NBT_PRESCALER=1 NBT_TSEG1=12 NBT_TSEG2=4 DBT_PRESCALER=1 DBT_TSEG1=3 DBT_TSEG2=1 TEST_MODULES=tests.test_timing_matrix'

run regress make -f Makefile.regress
run xval_model     python3 scripts/xval_ctu_full.py
run mutation_model python3 scripts/mutation_model.py

echo; echo "================ SUMMARY ================"; cat "$SUM"
echo; echo "================ CASE COUNTS ================"
grep -h -E "cases, [0-9]+ failures|PASS [0-9]+/[0-9]+ |cases found" logs/big_*.log logs/ctu_*.log logs/bnd_*.log 2>/dev/null | sed 's/^[^ ]* *//'
echo; echo "================ MODEL GATES ================"
grep -E "^MATCHED|^MISMATCH|^DEFERRED" logs/xval_model.log 2>/dev/null
grep -E "killed:|PROBLEMS" logs/mutation_model.log 2>/dev/null
echo
F=$(grep -c '^FAIL' "$SUM" || true)
echo "TOTAL FAILURES: $F   (logs in ./logs/)"
exit "$F"
