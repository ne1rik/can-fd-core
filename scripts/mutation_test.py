#!/usr/bin/env python3
"""Mutation testing for the CAN FD RTL.

Each mutant deliberately breaks one RTL property (CRC polynomial, stuffing
threshold, CRC init, CRC-width selection). The regression must FAIL on every
mutant. A mutant that survives means the test suite is not actually checking
that property, regardless of what coverage says.

Requires rtl/ to be committed (uses it as the restore point).
"""

import pathlib
import shutil
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent


class Mutant:
    def __init__(self, name, path, old, new, desc):
        self.name, self.path, self.old, self.new, self.desc = name, path, old, new, desc


MUTANTS = [
    Mutant("tx_crc17_poly", "rtl/can_fd_tx.sv",
           "21'h102899 : 21'h1685B", "21'h102899 : 21'h1685A",
           "TX CRC-17 polynomial LSB flipped"),
    Mutant("tx_crc21_poly", "rtl/can_fd_tx.sv",
           "21'h102899", "21'h102898",
           "TX CRC-21 polynomial LSB flipped"),
    Mutant("rx_crc17_poly", "rtl/can_fd_rx.sv",
           "sh ^ 17'h1685B", "sh ^ 17'h1685A",
           "RX CRC-17 polynomial LSB flipped"),
    Mutant("tx_stuff_threshold", "rtl/can_fd_tx.sv",
           "run_cnt == 3'd4", "run_cnt == 3'd3",
           "TX inserts stuff bit after 4 identical bits instead of 5"),
    Mutant("rx_stuff_threshold", "rtl/can_fd_rx.sv",
           "run_len == 3'd4", "run_len == 3'd3",
           "RX expects stuff bit after 4 identical bits instead of 5"),
    Mutant("tx_crc_init", "rtl/can_fd_tx.sv",
           "21'h100000:21'h010000", "21'h000000:21'h00000",
           "TX CRC initialized to zero instead of MSB-set"),
    Mutant("rx_crc17_init", "rtl/can_fd_rx.sv",
           "crc17_step(17'h10000,  1'b0)", "crc17_step(17'h00000,  1'b0)",
           "RX CRC-17 initialized to zero instead of MSB-set"),
    Mutant("tx_crc_width", "rtl/can_fd_tx.sv",
           "(dlc_reg>=4'd11)", "(dlc_reg>=4'd13)",
           "TX CRC-21 threshold reverted to the old bug (>=13)"),
    Mutant("rx_crc_width", "rtl/can_fd_rx.sv",
           "(rx_dlc >= 4'd11)", "(rx_dlc >= 4'd13)",
           "RX CRC-21 threshold reverted to the old bug (>=13)"),
]


def rtl_clean():
    r = subprocess.run(["git", "status", "--porcelain", "rtl/"],
                       capture_output=True, text=True, cwd=ROOT)
    return r.stdout.strip() == ""


def run_regression():
    """True if the full oracle passes. Oracle = TX-vs-model + loopback."""
    for builddir in ("sim_build_tx", "sim_build_loopback"):
        shutil.rmtree(ROOT / builddir, ignore_errors=True)
    for cmd in (["make"], ["make", "-f", "Makefile.loopback"]):
        p = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
        if p.returncode != 0:
            return False
    return True


def main():
    if not rtl_clean():
        print("rtl/ has uncommitted changes; commit first so mutants can be reverted", file=sys.stderr)
        return 2

    results = []
    for m in MUTANTS:
        path = ROOT / m.path
        original = path.read_text()
        count = original.count(m.old)
        if count == 0:
            results.append((m.name, "SKIP", "target string not found"))
            print(f"[SKIP] {m.name}: target not found in {m.path}")
            continue

        path.write_text(original.replace(m.old, m.new))
        print(f"[....] {m.name}: {m.desc}", flush=True)
        try:
            passed = run_regression()
            status = "SURVIVED" if passed else "KILLED"
        except Exception as exc:
            status = "ERROR"
            print(f"       runner error: {exc}")
        finally:
            path.write_text(original)   # always restore
        results.append((m.name, status, m.desc))
        print(f"[{status}] {m.name}")

    print()
    print(f"{'MUTANT':24s} {'RESULT':10s} DESCRIPTION")
    print("-" * 78)
    for name, status, desc in results:
        print(f"{name:24s} {status:10s} {desc}")

    applied = [r for r in results if r[1] in ("KILLED", "SURVIVED")]
    killed = [r for r in applied if r[1] == "KILLED"]
    survived = [r for r in applied if r[1] == "SURVIVED"]
    skipped = [r for r in results if r[1] == "SKIP"]

    print("-" * 78)
    print(f"kill rate: {len(killed)}/{len(applied)}"
          + (f"  (skipped {len(skipped)})" if skipped else ""))

    if survived:
        print("\nSURVIVING MUTANTS — the suite does NOT catch these faults:")
        for name, _, desc in survived:
            print(f"  - {name}: {desc}")
        return 1
    if skipped and not applied:
        return 2
    print("\nall mutants killed: the regression genuinely checks these properties")
    return 0


if __name__ == "__main__":
    sys.exit(main())
