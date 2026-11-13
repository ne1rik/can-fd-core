# Dependency smoke report

Generated: 2026-11-13 11:17 UTC
Host: Linux 6.6.87.2-microsoft-standard-WSL2 x86_64
OS: Ubuntu 20.04.6 LTS

| Status | Component | Version | Note |
|---|---|---|---|
| PASS | python3 | 3.12.10 | interpreter |
| PASS | make | GNU Make 4.2.1 | build tool |
| PASS | g++ | g++ (Ubuntu 9.4.0-1ubuntu1~20.04.2) 9.4.0 | build tool |
| PASS | git | git version 2.25.1 | build tool |
| PASS | verilator | Verilator 5.055 devel rev v5.054-219-g12ce86083 (mod) | simulator |
| PASS | cocotb | 2.1.0 | python package |
| PASS | pytest | 9.2.0 | python package |
| PASS | cocotb-coverage | 2.0 | OK version=2.0 coverpoint=smoke.dlc bins=16 coverage=16.0% |
| PASS | verilator --coverage | Verilator 5.055 devel rev v5.054-219-g12ce86083 (mod) | flag accepted |
| PASS | verilator --coverage-line | Verilator 5.055 devel rev v5.054-219-g12ce86083 (mod) | flag accepted |
| PASS | verilator --coverage-toggle | Verilator 5.055 devel rev v5.054-219-g12ce86083 (mod) | flag accepted |
| PASS | verilator --coverage-user | Verilator 5.055 devel rev v5.054-219-g12ce86083 (mod) | flag accepted |
| PASS | verilator --coverage-branch | Verilator 5.055 devel rev v5.054-219-g12ce86083 (mod) | flag accepted |
| PASS | verilator --coverage-expr | Verilator 5.055 devel rev v5.054-219-g12ce86083 (mod) | flag accepted |
| PASS | verilator --coverage-fsm | Verilator 5.055 devel rev v5.054-219-g12ce86083 (mod) | flag accepted |
| PASS | yosys | Yosys 0.70+385 (git sha1 098e46a36, Release, Cla | synthesis / formal front-end |
| PASS | sby | SBY v0.70-9-g79fc9ed | formal driver |
| PASS | yosys-smtbmc | present | formal engine / solver |
| PASS | yosys-abc | present | formal engine / solver |
| PASS | z3 | present | formal engine / solver |
| PASS | yices | present | formal engine / solver |
| PASS | boolector | present | formal engine / solver |
| PASS | formal run (smtbmc) | - | trivial proof completed |
| WARN | gtkwave | present | version probe inconclusive |

FAIL=0 WARN=1

## Toolchain upgrade — OSS CAD Suite

**Problem:** Yosys 0.9 (from Ubuntu 20.04 apt) is incompatible with sby v0.71.
The flag `hierarchy -smtcheck` is not recognized by Yosys 0.9.

**Solution:** Installed OSS CAD Suite 2024-09-19 from
https://github.com/YosysHQ/oss-cad-suite-build/releases. This package provides:
- Yosys 0.44+ (fresh enough for sby v0.71)
- sby v0.71
- Solvers: yices, boolector, z3
- All added to PATH via `export PATH="$HOME/oss-cad-suite/bin:$PATH"`

**Result:** Formal verification smoke test now passes. All dependencies are
verified and documented in this report.

## Финальный статус тулчейна (после установки OSS CAD Suite)

**Результат:** `FAIL=0 WARN=1` (gtkwave WARN не влияет на CI/регрессию).
- **Yosys 0.70+** успешно выполняет `-smtcheck` и работает с `sby v0.70+`.
- **Все флаги покрытия Verilator** (`--coverage`, `--coverage-line`, `--coverage-toggle`, `--coverage-user`, `--coverage-branch`, `--coverage-expr`, `--coverage-fsm`) теперь **PASS**.
- **Решатели** `z3`, `yices`, `boolector` доступны и готовы к использованию в SymbiYosys.
- **cocotb-coverage 2.0** успешно интегрирован и проходит smoke-тест coverpoint'ов.

Тулчейн полностью соответствует требованиям M1 и готов к формальной верификации и сборке функционального покрытия.
