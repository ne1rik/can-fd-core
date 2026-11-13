# Pinned toolchain

Local development and CI must use the SAME simulator version.

| Tool | Version | Source |
|---|---|---|
| Verilator | **5.036** | built from source, installed to `/usr/local/bin` |
| cocotb | 2.1.0 | pip (pyenv Python 3.12) |
| cocotb-coverage | 2.0 | pip |
| Yosys | 0.70+ | OSS CAD Suite |
| sby | 0.70+ | OSS CAD Suite |
| solvers (z3/yices/boolector) | bundled | OSS CAD Suite |

## Known conflict: OSS CAD Suite shadows Verilator and cocotb

OSS CAD Suite ships its own `verilator` (5.055 devel) and `cocotb`
(2.1.0.dev0, built against GLIBC 2.38). Both break this project on
Ubuntu 20.04:

* its cocotb fails with `GLIBC_2.38 not found`;
* its Verilator exposes wide packed vectors differently over VPI, so
  `dut.tx_data.value = <int>` raises `TypeError: object of type 'int' has no len()`.

**Resolution:** keep only Yosys / sby / solvers from OSS CAD Suite and remove
its `verilator*` and `cocotb*` binaries, so the verified source build and the
pip-installed cocotb are used instead.

```bash
rm -f  ~/oss-cad-suite/bin/cocotb* ~/oss-cad-suite/libexec/cocotb-config
rm -rf ~/oss-cad-suite/lib/python3.11/site-packages/cocotb*
rm -f  ~/oss-cad-suite/bin/verilator*
rm -rf ~/oss-cad-suite/share/verilator
hash -r
```
verilator --version   # must be 5.036
cocotb-config --version  # must be 2.1.0
```
