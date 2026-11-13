# Dependency smoke report

Generated: 2026-11-13 11:09 UTC
Host: Linux 6.6.87.2-microsoft-standard-WSL2 x86_64
OS: Ubuntu 20.04.6 LTS

| Status | Component | Version | Note |
|---|---|---|---|
| PASS | python3 | 3.12.10 | interpreter |
| PASS | make | GNU Make 4.2.1 | build tool |
| PASS | g++ | g++ (Ubuntu 9.4.0-1ubuntu1~20.04.2) 9.4.0 | build tool |
| PASS | git | git version 2.25.1 | build tool |
| PASS | verilator | Verilator 5.036 2025-04-27 rev v5.036 | simulator |
| PASS | cocotb | 2.1.0 | python package |
| PASS | pytest | 9.2.0 | python package |
| PASS | cocotb-coverage | 2.0 | OK version=2.0 coverpoint=smoke.dlc bins=16 coverage=16.0% |
| PASS | verilator --coverage | Verilator 5.036 2025-04-27 rev v5.036 | flag accepted |
| PASS | verilator --coverage-line | Verilator 5.036 2025-04-27 rev v5.036 | flag accepted |
| PASS | verilator --coverage-toggle | Verilator 5.036 2025-04-27 rev v5.036 | flag accepted |
| PASS | verilator --coverage-user | Verilator 5.036 2025-04-27 rev v5.036 | flag accepted |
| WARN | verilator --coverage-branch | Verilator 5.036 2025-04-27 rev v5.036 | flag rejected by this build |
| PASS | verilator --coverage-expr | Verilator 5.036 2025-04-27 rev v5.036 | flag accepted |
| WARN | verilator --coverage-fsm | Verilator 5.036 2025-04-27 rev v5.036 | flag rejected by this build |
| PASS | yosys | Yosys 0.9 (git sha1 1979e0b) | synthesis / formal front-end |
| PASS | sby | SBY v0.71 | formal driver |
| PASS | yosys-smtbmc | present | formal engine / solver |
| PASS | yosys-abc | present | formal engine / solver |
| PASS | z3 | present | formal engine / solver |
| WARN | yices | absent | may be required by the chosen engine |
| WARN | boolector | absent | may be required by the chosen engine |
| FAIL | formal run (smtbmc) | - | SBY 14:09:37 [smoke_formal] DONE (ERROR, rc=16) |
| PASS | gtkwave | GTKWave Analyzer v3.3.103 (w)1999-2019 BSI | waveform viewer |

FAIL=1 WARN=4

## Coverage flags — actual support in Verilator 5.036

| Flag | Status | Notes |
|---|---|---|
| `--coverage` | PASS | Enables line + branch + toggle coverage |
| `--coverage-line` | PASS | Line coverage only |
| `--coverage-toggle` | PASS | Toggle coverage only |
| `--coverage-user` | PASS | User-defined coverage points |
| `--coverage-expr` | PASS | Expression coverage |
| `--coverage-branch` | WARN | Not a separate flag in 5.036; use `--coverage` |
| `--coverage-fsm` | WARN | Not supported in 5.036 |

**Action:** Update project documentation and CI scripts to use `--coverage` instead of `--coverage-branch`. FSM coverage is not available in the current toolchain version.
