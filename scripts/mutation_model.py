import os
import json
#!/usr/bin/env python3
"""Mutation testing of the reference MODEL, oracle = CTU cross-validation.

Each mutant declares its EXPECTED outcome:
  KILLED   - the CTU oracle must catch it (a real checked property)
  SURVIVED - a KNOWN ORACLE GAP; surviving is the expected, documented result

An unexpected SURVIVED is a failure. An unexpected KILLED means a gap closed
and the expectation should be updated.

Requires tb/can_fd_reference.py to be committed (restore point).
"""
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
MODEL = "tb/can_fd_reference.py"


class M:
    def __init__(self, name, old, new, desc, expect="KILLED"):
        self.name, self.old, self.new, self.desc, self.expect = name, old, new, desc, expect


MUTANTS = [
    # --- Classic CAN ---
    M("classic_crc_over_stuffed",
      "crc = _crc_val(raw, 15, 0x4599, 0)",
      "crc = _crc_val(stuff_bits(raw)[0], 15, 0x4599, 0)",
      "Classic CRC-15 over STUFFED stream (the real bug we fixed)"),
    M("classic_crc_not_stuffed",
      "st, pos = stuff_bits(raw_with_crc)",
      "st, pos = stuff_bits(raw); st = st + cb",
      "Classic CRC field left unstuffed"),
    M("classic_crc_poly_lsb",
      "crc = _crc_val(raw, 15, 0x4599, 0)",
      "crc = _crc_val(raw, 15, 0x4598, 0)",
      "Classic CRC-15 polynomial LSB flipped"),
    M("classic_crc_init_msb",
      "crc = _crc_val(raw, 15, 0x4599, 0)",
      "crc = _crc_val(raw, 15, 0x4599, 1 << 14)",
      "Classic CRC init MSB-set (FD convention leaked)"),

    # --- FEFF geometry (single-line unique targets) ---
    M("feff_drop_res_bit",
      "r += [0, 1, 0]  # RRS=0, FDF=1, res=0",
      "r += [0, 1]  # mutant: res dropped",
      "FEFF reserved bit removed (40-bit header instead of 41)"),
    M("feff_rrs_dominant",
      "r += [0, 1, 0]  # RRS=0, FDF=1, res=0",
      "r += [1, 1, 0]  # mutant: RRS dominant",
      "FEFF RRS driven dominant instead of recessive"),

    # --- shared FD machinery ---
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
    M("fd_crc17_poly_lsb",
      "w, poly = (21, 0x102899) if n > 16 else (17, 0x1685B)",
      "w, poly = (21, 0x102899) if n > 16 else (17, 0x1685A)",
      "CRC-17 polynomial LSB flipped"),

    # --- KNOWN ORACLE GAP: no DLC>=11 frame exists in the BRS=0 corpus ---
    M("fd_crc21_poly_lsb",
      "w, poly = (21, 0x102899) if n > 16 else (17, 0x1685B)",
      "w, poly = (21, 0x102898) if n > 16 else (17, 0x1685B)",
      "CRC-21 polynomial LSB flipped",
      expect="KILLED"),
]


def clean():
    r = subprocess.run(["git", "status", "--porcelain", MODEL],
                       capture_output=True, text=True, cwd=ROOT)
    return r.stdout.strip() == ""


ENV_ORACLE = dict(os.environ)
ENV_ORACLE["PYTHONDONTWRITEBYTECODE"] = "1"  # оракул не создаёт pyc (анти-отравление)

def _purge_model_pyc():
    pc = (ROOT / MODEL).parent / "__pycache__"
    if pc.exists():
        for _p in pc.glob((ROOT / MODEL).stem + ".*.pyc"):
            _p.unlink()

def oracle():
    p = subprocess.run([sys.executable, "scripts/xval_ctu_full.py",
                        "--only", "1", "--out", "coverage/_mut"],
                       capture_output=True, text=True, cwd=ROOT, env=ENV_ORACLE)
    q = subprocess.run([sys.executable, "scripts/crc21_golden_check.py", "--check"],
                       capture_output=True, text=True, cwd=ROOT, env=ENV_ORACLE)
    if q.returncode != 0:
        out = (q.stdout or q.stderr).strip()
        print("       golden-check:", out.splitlines()[-1] if out else "exit %d" % q.returncode)
    return (p.returncode == 0) and (q.returncode == 0)


def main():
    if not clean():
        print(f"{MODEL} has uncommitted changes; commit first", file=sys.stderr)
        return 2

    path = ROOT / MODEL
    original = path.read_text()
    
    # E18: Fail-closed check. Ensure fixture exists and matches pristine model MD5.
    import hashlib, json
    fixture_path = ROOT / "coverage" / "crc21_golden.json"
    if not fixture_path.exists():
        print("FATAL: crc21_golden.json missing. Run scripts/crc21_golden_check.py --freeze first.", file=sys.stderr)
        sys.exit(2)
    fixture_data = json.loads(fixture_path.read_text())
    current_md5 = hashlib.md5(path.read_bytes()).hexdigest()
    if fixture_data.get("model_md5") != current_md5:
        print(f"FATAL: Fixture MD5 mismatch! Expected {fixture_data.get('model_md5')}, got {current_md5}.", file=sys.stderr)
        sys.exit(2)
    
    rows = []
    problems = []

    
    # CRC-21 дыра закрыта scripts/crc21_golden_check.py (fixture-оракул).
    # Инъекция удалена: xval пересобирает ctu_vectors_all.json и стирал кадры (0x16b=0).
    
    for m in MUTANTS:
        n = original.count(m.old)
        if n != 1:
            rows.append((m.name, "SKIP", f"target matches={n}", m.desc))
            print(f"[SKIP] {m.name}: target matches={n}")
            problems.append(m.name)
            continue

        _purge_model_pyc()  # purge ДО записи мутанта (pyc-коллизия same second + same size)
        path.write_text(original.replace(m.old, m.new))
        print(f"[....] {m.name}", flush=True)
        try:
            status = "SURVIVED" if oracle() else "KILLED"
        except Exception as e:
            status = "ERROR"
            print(f"       {e}")
        finally:
            path.write_text(original)
            _st = path.stat()
            os.utime(path, ns=(_st.st_atime_ns, _st.st_mtime_ns + 1_000_000_000))  # break mtime-second equality with pyc header
            _pc = path.parent / '__pycache__'
            if _pc.exists():
                for _p in _pc.glob(path.stem + '.*.pyc'):
                    _p.unlink()
            if path.read_text() != original:
                raise RuntimeError('MODEL NOT RESTORED byte-exact: %s' % path)

        if status == m.expect:
            tag = "KILLED" if status == "KILLED" else "GAP-CONFIRMED"
        elif status == "KILLED" and m.expect == "SURVIVED":
            tag = "GAP-CLOSED"
            print(f"       NOTE: gap closed for {m.name}; update expectation")
        else:
            tag = "UNEXPECTED-SURVIVAL"
            problems.append(m.name)
        rows.append((m.name, tag, m.expect, m.desc))
        print(f"[{tag}] {m.name}")

    print()
    print(f"{'MUTANT':26s} {'RESULT':20s} {'EXPECT':10s} DESCRIPTION")
    print("-" * 104)
    for name, tag, exp, desc in rows:
        print(f"{name:26s} {tag:20s} {exp:10s} {desc}")

    killed = sum(1 for r in rows if r[1] == "KILLED")
    gaps = sum(1 for r in rows if r[1] == "GAP-CONFIRMED")
    print("-" * 104)
    print(f"killed: {killed}   documented gaps: {gaps}   problems: {len(problems)}")
    if problems:
        print("PROBLEMS: " + ", ".join(problems))
        return 1
    print("\nall expectations met (gaps are documented, not hidden)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
