#!/usr/bin/env python3
"""Mutation testing of the reference MODEL, oracle = CTU cross-validation.

Rationale: RTL does not yet implement Classic/FEFF, so RTL mutants cannot
cover that code. The model does, and the CTU corpus is an independent oracle.
A surviving mutant means the xval gate does not actually check that property.

Requires tb/can_fd_reference.py to be committed (restore point).
"""
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
MODEL = "tb/can_fd_reference.py"


class M:
    def __init__(self, name, old, new, desc):
        self.name, self.old, self.new, self.desc = name, old, new, desc


MUTANTS = [
    # --- Classic CAN: the exact bug we just fixed, plus neighbours ---
    M("classic_crc_over_stuffed",
      "crc = _crc_val(raw, 15, 0x4599, 0)",
      "crc = _crc_val(stuff_bits(raw)[0], 15, 0x4599, 0)",
      "Classic CRC-15 computed over STUFFED stream (the real bug)"),
    M("classic_crc_not_stuffed",
      "st, pos = stuff_bits(raw_with_crc)",
      "st, pos = stuff_bits(raw); st = st + cb",
      "Classic CRC appended after stuffing (CRC field left unstuffed)"),
    M("classic_crc_poly_lsb",
      "crc = _crc_val(raw, 15, 0x4599, 0)",
      "crc = _crc_val(raw, 15, 0x4598, 0)",
      "Classic CRC-15 polynomial LSB flipped"),
    M("classic_crc_init_msb",
      "crc = _crc_val(raw, 15, 0x4599, 0)",
      "crc = _crc_val(raw, 15, 0x4599, 1 << 14)",
      "Classic CRC init MSB-set instead of 0 (FD convention leaked)"),

    # --- FEFF geometry ---
    M("feff_drop_res_bit",
      "r += [0, 1, 0]  # RRS=0, FDF=1, res=0",
      "r += [0, 1]  # mutant: res dropped",
      "FEFF reserved bit removed (40-bit header instead of 41)"),
    M("feff_srr_dominant",
      "        r += [1, 1]  # SRR, IDE\n"
      "        r += [(fid >> i) & 1 for i in range(17, -1, -1)]  # ID B[17:0]\n"
      "        r += [0, 1, 0]  # RRS=0, FDF=1, res=0",
      "        r += [0, 1]  # mutant: SRR dominant\n"
      "        r += [(fid >> i) & 1 for i in range(17, -1, -1)]  # ID B[17:0]\n"
      "        r += [0, 1, 0]  # RRS=0, FDF=1, res=0",
      "FEFF SRR driven dominant instead of recessive"),

    # --- FBFF / shared machinery ---
    M("sbc_odd_parity",
      "bits.append(sum(bits) % 2)",
      "bits.append(1 - sum(bits) % 2)",
      "Stuff-count parity flipped to odd"),
    M("fsb_interval_five",
      "        i += 4",
      "        i += 5",
      "Fixed stuff bits every 5 bits instead of 4"),
    M("fd_crc_init_zero",
      "crc = _crc_val(st + sc, w, poly, 1 << (w - 1))",
      "crc = _crc_val(st + sc, w, poly, 0)",
      "CAN FD CRC init zero instead of MSB-set"),
    M("stuff_run_reset_zero",
      "last, run = sb, 1",
      "last, run = sb, 0",
      "Stuff bit does not start the next run"),
]


def clean():
    r = subprocess.run(["git", "status", "--porcelain", MODEL],
                       capture_output=True, text=True, cwd=ROOT)
    return r.stdout.strip() == ""


def oracle():
    """True if CTU cross-validation passes (dataset 1, all formats)."""
    p = subprocess.run([sys.executable, "scripts/xval_ctu_full.py",
                        "--only", "1", "--out", "coverage/_mut"],
                       capture_output=True, text=True, cwd=ROOT)
    return p.returncode == 0


def main():
    if not clean():
        print(f"{MODEL} has uncommitted changes; commit first", file=sys.stderr)
        return 2

    path = ROOT / MODEL
    original = path.read_text()
    results = []

    for m in MUTANTS:
        n = original.count(m.old)
        if n == 0:
            results.append((m.name, "SKIP", "target not found"))
            print(f"[SKIP] {m.name}: target not found")
            continue
        if n > 1:
            results.append((m.name, "SKIP", f"ambiguous target ({n} matches)"))
            print(f"[SKIP] {m.name}: ambiguous target ({n} matches)")
            continue

        path.write_text(original.replace(m.old, m.new))
        print(f"[....] {m.name}", flush=True)
        try:
            status = "SURVIVED" if oracle() else "KILLED"
        except Exception as e:
            status = "ERROR"
            print(f"       {e}")
        finally:
            path.write_text(original)
        results.append((m.name, status, m.desc))
        print(f"[{status}] {m.name}")

    print()
    print(f"{'MUTANT':28s} {'RESULT':10s} DESCRIPTION")
    print("-" * 90)
    for name, st, desc in results:
        print(f"{name:28s} {st:10s} {desc}")

    applied = [r for r in results if r[1] in ("KILLED", "SURVIVED")]
    killed = [r for r in applied if r[1] == "KILLED"]
    survived = [r for r in applied if r[1] == "SURVIVED"]
    skipped = [r for r in results if r[1] == "SKIP"]

    print("-" * 90)
    print(f"kill rate: {len(killed)}/{len(applied)}"
          + (f"  (skipped {len(skipped)})" if skipped else ""))
    if survived:
        print("\nSURVIVING — the xval gate does NOT check these:")
        for name, _, desc in survived:
            print(f"  - {name}: {desc}")
        return 1
    if not applied:
        return 2
    print("\nall model mutants killed by the CTU oracle")
    return 0


if __name__ == "__main__":
    sys.exit(main())
