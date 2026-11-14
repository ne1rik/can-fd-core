#!/usr/bin/env python3
"""Full CTU cross-validation: 10 datasets x 4 frame formats.

Criterion (identical to the per-format checks):
  * bits up to and including the CRC delimiter must match exactly
  * ACK slot: CTU=0 (receiver drives dominant), ours=1 (transmitter view)
  * everything after ACK is recessive (ACK del + EOF + idle padding)

Scope: data frames (rtr=0), no injected error (erf=0), ESI=0.
CAN FD with BRS=1 is DEFERRED: our simulation is single-phase, so the CTU
two-rate waveform is not comparable yet. Reported explicitly, never hidden.

Also emits a model-level format coverage report from the same corpus.
Exit code: 0 if no mismatch, 1 otherwise.
"""
import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tb"))
sys.path.insert(0, str(ROOT / "scripts"))

from can_fd_reference import generate_can_fd_frame, dlc_len
from xval_ctu_wave_diag import tuples, fields, expand

REF_DIR = ROOT.parent / "ctu-can-fd-ref/test/main_tb/reference_test_data_sets"


def fmt_name(ff, it):
    if ff == 1:
        return "fd_ext" if it == 1 else "fd_base"
    return "classic_ext" if it == 1 else "classic_base"


def classify_pattern(data):
    if not data or all(b == 0 for b in data):
        return "zeros"
    if all(b == 0xFF for b in data):
        return "ones"
    if all(b == (0xAA if i % 2 == 0 else 0x55) for i, b in enumerate(data)):
        return "alternating"
    if all(b == (i & 0xFF) for i, b in enumerate(data)):
        return "ramp"
    return "random"


def verdict(ours, ctu):
    L = len(ours)
    if len(ctu) < L:
        return "ctu_shorter", None
    pre = L - 9
    if ctu[:pre] != ours[:pre]:
        k = next(i for i, (a, b) in enumerate(zip(ctu[:pre], ours[:pre])) if a != b)
        return "prefix_mismatch", k
    if ctu[pre] != 0 or ours[pre] != 1:
        return "ack_unexpected", pre
    if any(b != 1 for b in ctu[pre + 1:]):
        return "tail_not_idle", pre + 1
    return "ACK_ONLY_DIFF", None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", type=int, default=0, help="single dataset number, 0 = all")
    ap.add_argument("--out", default="coverage/xval_full")
    args = ap.parse_args()

    nums = [args.only] if args.only else range(1, 11)
    stats = Counter()
    per_ds = {}
    failures = []
    
    # Coverage counters
    cov_fmt = Counter()
    cov_crc = Counter()
    cov_dlc = Counter()
    cov_pat = Counter()
    cross_fmt_crc = Counter()
    cross_fmt_pat = Counter()
    
    # Deferred counters
    def_crc = Counter()
    def_dlc = Counter()

    for n in nums:
        path = REF_DIR / f"reference_data_set_{n}.vhd"
        if not path.exists():
            print(f"MISSING {path}", file=sys.stderr)
            return 2
        ds = Counter()
        for t in tuples(path.read_text()):
            f, seq = fields(t)
            if f['ff'] is None or f['dlc'] is None or f['id'] is None:
                ds['unparsed'] += 1
                continue
            if f['rtr'] != 0 or f['erf'] != 0 or f['esi'] != 0:
                ds['out_of_scope'] += 1
                continue

            name = fmt_name(f['ff'], f['it'])
            classic = (f['ff'] == 0)
            ext = (f['it'] == 1)

            if not classic and f['brs'] == 1:
                ds[f'{name}:deferred_brs1'] += 1
                stats[f'{name}:deferred_brs1'] += 1
                
                nb_d = dlc_len(f['dlc'], classic=False)
                def_crc['crc21' if nb_d > 16 else 'crc17'] += 1
                def_dlc[f'dlc{f["dlc"]}'] += 1
                continue

            nb = dlc_len(f['dlc'], classic=classic)
            data = (f['data'] + [0] * nb)[:nb]
            ours = generate_can_fd_frame(f['id'], f['dlc'], data, False,
                                         extended=ext, classic=classic)
            v, k = verdict(ours, expand(seq))
            ds[f'{name}:{v}'] += 1
            stats[f'{name}:{v}'] += 1

            if v == "ACK_ONLY_DIFF":
                w = 15 if classic else (21 if nb > 16 else 17)
                pat = classify_pattern(data)
                cov_fmt[name] += 1
                cov_crc[f'crc{w}'] += 1
                cov_dlc[f'dlc{f["dlc"]}'] += 1
                cov_pat[pat] += 1
                cross_fmt_crc[(name, f'crc{w}')] += 1
                cross_fmt_pat[(name, pat)] += 1
            elif len(failures) < 20:
                failures.append({"dataset": n, "format": name, "id": f['id'],
                                 "dlc": f['dlc'], "verdict": v, "first_diff": k})
        per_ds[n] = dict(ds)
        print(f"dataset {n:2d}: {dict(ds)}")

    total_ok = sum(v for k, v in stats.items() if k.endswith(':ACK_ONLY_DIFF'))
    total_bad = sum(v for k, v in stats.items()
                    if not k.endswith(':ACK_ONLY_DIFF') and not k.endswith(':deferred_brs1'))
    total_def = sum(v for k, v in stats.items() if k.endswith(':deferred_brs1'))

    report = {
        "scope": "data frames, erf=0, esi=0; CAN FD BRS=1 deferred (single-phase sim)",
        "per_dataset": per_ds,
        "totals": dict(stats),
        "matched": total_ok,
        "mismatched": total_bad,
        "deferred_brs1": total_def,
        "deferred_crc": dict(def_crc),
        "deferred_dlc": dict(sorted(def_dlc.items(), key=lambda x: int(x[0][3:]))),
        "model_format_coverage": {
            "format": dict(cov_fmt),
            "crc_width": dict(cov_crc),
            "dlc": dict(sorted(cov_dlc.items(), key=lambda x: int(x[0][3:]))),
            "pattern": dict(cov_pat),
            "format_x_crc": {f"{a}|{b}": c for (a, b), c in sorted(cross_fmt_crc.items())},
            "format_x_pattern": {f"{a}|{b}": c for (a, b), c in sorted(cross_fmt_pat.items())},
        },
        "failures": failures,
    }
    out = ROOT / args.out
    out.parent.mkdir(exist_ok=True)
    Path(str(out) + ".json").write_text(json.dumps(report, indent=1, sort_keys=True))

    L = ["# CTU Full Cross-Validation", "",
         f"**Matched (ACK-only diff): {total_ok}**", 
         f"**Mismatched: {total_bad}**",
         f"**Deferred (FD BRS=1, needs two-phase timing): {total_def}**", "",
         "## Per format", "", "| Format | Verdict | Count |", "|---|---|---|"]
    for k, v in sorted(stats.items()):
        a, b = k.split(":", 1)
        L.append(f"| {a} | {b} | {v} |")
    
    L += ["", "## Model-level format coverage (from CTU corpus)", "",
          "| Format | Frames |", "|---|---|"]
    for k, v in sorted(cov_fmt.items()):
        L.append(f"| {k} | {v} |")
    
    L += ["", "| CRC width | Frames |", "|---|---|"]
    for k, v in sorted(cov_crc.items()):
        L.append(f"| {k} | {v} |")
    
    L += ["", "| Format x CRC | Frames |", "|---|---|"]
    for (a, b), c in sorted(cross_fmt_crc.items()):
        L.append(f"| {a} x {b} | {c} |")
    
    L += ["", "## Deferred (FD BRS=1) breakdown", "",
          "| CRC width | Deferred frames |", "|---|---|"]
    for k, v in sorted(def_crc.items()):
        L.append(f"| {k} | {v} |")
    
    L += ["", "| DLC | Deferred frames |", "|---|---|"]
    for k, v in sorted(def_dlc.items(), key=lambda x: int(x[0][3:])):
        L.append(f"| {k} | {v} |")
    
    missing = sorted({"crc15", "crc17", "crc21"} - set(cov_crc))
    L += ["", "## VALIDATION GAP", ""]
    if missing:
        L.append(f"CRC widths with ZERO independent waveform confirmation: **{', '.join(missing)}**")
        L.append("")
        L.append("These widths appear only in the deferred BRS=1 subset. Two-phase bit")
        L.append("timing (sample point + SSP) is required to close this gap.")
    else:
        L.append("All CRC widths independently confirmed.")
    
    L += ["", "NOTE: RTL coverage remains FBFF-scoped until RTL supports all formats.", ""]
    
    if failures:
        L += ["## Failures (first 20)", ""]
        for f in failures:
            L.append(f"- ds{f['dataset']} {f['format']} id={f['id']:#x} "
                     f"dlc={f['dlc']} {f['verdict']} @ {f['first_diff']}")
    
    Path(str(out) + ".md").write_text("\n".join(L) + "\n")

    print()
    print(f"MATCHED   {total_ok}")
    print(f"MISMATCH  {total_bad}")
    print(f"DEFERRED  {total_def}  (FD BRS=1)")
    print(f"report: {out}.md / .json")
    return 1 if total_bad else 0


if __name__ == "__main__":
    sys.exit(main())
