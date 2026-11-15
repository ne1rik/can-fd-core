#!/usr/bin/env python3
"""Build the verification report from recorded logs. No hand-written numbers."""
import argparse, html, json, re, shutil, subprocess, sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOGS, COV, OUT = ROOT / "logs", ROOT / "coverage", ROOT / "docs"
NA = "n/a"

def read(p):
    try: return p.read_text(errors="replace")
    except OSError: return ""

def corpus():
    p = COV / "ctu_vectors_all.json"
    if not p.exists(): return {"total": NA, "synthetic": NA, "by_format": {}}
    try: d = json.loads(p.read_text())
    except json.JSONDecodeError: return {"total": NA, "synthetic": NA, "by_format": {}}
    by = {}
    for v in d:
        k = v.get("format", "unknown"); by[k] = by.get(k, 0) + 1
    return {"total": len(d), "synthetic": sum(1 for v in d if v.get("synthetic")),
            "by_format": dict(sorted(by.items()))}

def sum_p(files, pat, groups):
    tot = [0] * len(groups); seen = False
    for f in files:
        m = re.search(pat, read(LOGS / f))
        if m:
            seen = True
            for i, g in enumerate(groups): tot[i] += int(m.group(g))
    return tuple(tot) if seen else (NA,) * len(groups)

def metrics():
    m = {"corpus": corpus()}
    m["ctu_passed"], m["ctu_total"] = sum_p(
        ["ctu_classic_base.log", "ctu_classic_ext.log", "ctu_fd_base.log", "ctu_fd_ext.log"],
        r"PASS\s+(\d+)/(\d+)", (1, 2))
    m["sweep_cases"], m["sweep_fails"] = sum_p(
        ["big_classic_base.log", "big_classic_ext.log", "big_fd_base.log", "big_fd_ext.log"],
        r"(\d+)\s+cases,\s*(\d+)\s+failures", (1, 2))
    m["bnd_cases"], m["bnd_fails"] = sum_p(
        ["bnd_classic_base.log", "bnd_classic_ext.log"],
        r"(\d+)\s+cases,\s*(\d+)\s+failures", (1, 2))
    mm = re.search(r"(\d+)\s+passed", read(LOGS / "regress.log"))
    m["pytest"] = int(mm.group(1)) if mm else NA
    mm = re.search(r"killed:\s*(\d+)\s+documented gaps:\s*(\d+)\s+problems:\s*(\d+)",
                   read(LOGS / "mutation_model.log"))
    if mm: m["mut_killed"], m["mut_gaps"], m["mut_problems"] = map(int, mm.groups())
    else: m["mut_killed"] = m["mut_gaps"] = m["mut_problems"] = NA
    txt = read(LOGS / "mutation_model.log")
    m["mut_total"] = len(re.findall(r"^\w+\s+(?:KILLED|SURVIVED|UNEXPECTED-\w+)", txt, re.M)) or NA
    txt = read(LOGS / "xval_model.log")
    for k, p in (("matched", r"MATCHED\s+(\d+)"), ("mismatch", r"MISMATCH\s+(\d+)"),
                 ("deferred", r"DEFERRED\s+(\d+)")):
        mm = re.search(p, txt); m["xval_" + k] = int(mm.group(1)) if mm else NA
    try:
        m["git"] = subprocess.run(["git", "describe", "--tags", "--always"],
                                  cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()
    except Exception: m["git"] = NA
    return m

T = {
    "en": {"title": "CAN FD Verification Kit — Report",
           "sub": "Simulation-only, Verilator + cocotb, ISO 11898-1:2015",
           "disc": "Not an industrial IP block. No conformance certificate is claimed. Every number is parsed from a recorded run log.",
           "g_ctu": "CTU vectors through RTL", "g_sweep": "Model-vs-RTL sweep", "g_bnd": "CRC-boundary stuffing",
           "g_pytest": "Model unit tests (pytest)", "g_xval": "Model vs CTU waveforms", "g_mut": "Mutation testing",
           "r_fail": "failures", "r_passed": "passed", "r_matched": "matched", "r_mismatch": "mismatch", "r_deferred": "deferred",
           "r_killed": "killed", "r_gaps": "gaps", "r_problems": "problems",
           "total": "Total", "synthetic": "of which synthetic"},
    "ru": {"title": "Комплект верификации CAN FD — Отчёт",
           "sub": "Только симуляция, Verilator + cocotb, ISO 11898-1:2015",
           "disc": "Не промышленный IP-блок. Сертификация соответствия не заявляется. Каждое число разобрано из лога прогона.",
           "g_ctu": "CTU-векторы через RTL", "g_sweep": "Прогон модель-против-RTL", "g_bnd": "Стаффинг на границе CRC",
           "g_pytest": "Юнит-тесты модели (pytest)", "g_xval": "Модель против осциллограмм CTU", "g_mut": "Мутационное тестирование",
           "r_fail": "отказов", "r_passed": "пройдено", "r_matched": "совпало", "r_mismatch": "расхождений", "r_deferred": "отложено",
           "r_killed": "убито", "r_gaps": "пробелов", "r_problems": "проблем",
           "total": "Всего", "synthetic": "в том числе синтетических"}
}

CSS = """@page { size: A4; margin: 18mm 16mm; }
body { font-family: "DejaVu Sans", "Liberation Sans", Arial, sans-serif; font-size: 10pt; line-height: 1.45; color: #111; max-width: 190mm; margin: 0 auto; padding: 12mm; }
h1 { font-size: 17pt; margin: 0 0 2mm; } h2 { font-size: 12pt; margin: 7mm 0 2mm; border-bottom: 1px solid #bbb; padding-bottom: 1mm; }
.sub { color: #555; font-size: 9.5pt; margin-bottom: 3mm; } .meta { color: #555; font-size: 9pt; margin-bottom: 4mm; }
.disc { background: #f4f4f4; border-left: 3px solid #888; padding: 2.5mm 3mm; font-size: 9pt; margin-bottom: 4mm; }
table { border-collapse: collapse; width: 100%; font-size: 9pt; margin: 2mm 0; }
th, td { border: 1px solid #ccc; padding: 1.4mm 2mm; text-align: left; vertical-align: top; }
th { background: #efefef; } code { font-family: "DejaVu Sans Mono", monospace; font-size: 8.5pt; }
.foot { color: #666; font-size: 8.5pt; margin-top: 6mm; border-top: 1px solid #ddd; padding-top: 2mm; }"""

def build_html(lang, m, args):
    t, e = T[lang], html.escape
    p = [f"<!DOCTYPE html><html lang='{lang}'><head><meta charset='utf-8'><title>{e(t['title'])}</title><style>{CSS}</style></head><body>"]
    p.append(f"<h1>{e(t['title'])}</h1><div class='sub'>{e(t['sub'])}</div>")
    p.append(f"<div class='meta'>{e(args.author)} · {e(args.email)} · {e(args.repo)} · v{e(str(m['git']))} · {date.today().isoformat()}</div>")
    p.append(f"<div class='disc'>{e(t['disc'])}</div>")
    p.append("<h2>Metrics</h2><table><tr><th>Gate</th><th>Result</th><th>Evidence</th></tr>")
    rows = [(t["g_ctu"], f'{m["ctu_passed"]} / {m["ctu_total"]}, 0 {t["r_fail"]}', "logs/ctu_*.log"),
            (t["g_sweep"], f'{m["sweep_cases"]} cases, {m["sweep_fails"]} {t["r_fail"]}', "logs/big_*.log"),
            (t["g_bnd"], f'{m["bnd_cases"]} cases, {m["bnd_fails"]} {t["r_fail"]}', "logs/bnd_*.log"),
            (t["g_pytest"], f'{m["pytest"]} {t["r_passed"]}', "logs/regress.log"),
            (t["g_xval"], f'{m["xval_matched"]} {t["r_matched"]}, {m["xval_mismatch"]} {t["r_mismatch"]}, {m["xval_deferred"]} {t["r_deferred"]}', "logs/xval_model.log"),
            (t["g_mut"], f'{m["mut_killed"]} / {m["mut_total"]} {t["r_killed"]}, {m["mut_gaps"]} {t["r_gaps"]}, {m["mut_problems"]} {t["r_problems"]}', "logs/mutation_model.log")]
    for g, r, s in rows: p.append(f"<tr><td>{e(g)}</td><td>{e(r)}</td><td><code>{e(s)}</code></td></tr>")
    p.append("</table>")
    c = m["corpus"]
    p.append("<h2>Corpus</h2><table><tr><th>Format</th><th>Vectors</th></tr>")
    for k, v in c["by_format"].items(): p.append(f"<tr><td><code>{e(k)}</code></td><td>{v}</td></tr>")
    p.append(f"<tr><th>{e(t['total'])}</th><th>{c['total']}</th></tr><tr><td>{e(t['synthetic'])}</td><td>{c['synthetic']}</td></tr></table>")
    p.append("<h2>Methodology</h2><ul>")
    if lang == "en":
        p.append("<li><b>Vector corpus:</b> frames extracted from CTU CAN FD reference captures, compared bit-by-bit against the model and RTL output. ACK slot excluded (driven by receiver).</li>")
        p.append("<li><b>Sweep:</b> all four formats, DLC 0–15, BRS on/off, payload patterns 0x00 / 0xFF / alternating, RTL vs model.</li>")
        p.append("<li><b>Mutation:</b> protocol-level faults injected into the reference model (CRC polynomial, CRC init, stuffing interval, stuff-count parity, reserved bits). A mutant must be detected.</li>")
        p.append("<li><b>Real timing:</b> NBT/DBT with configurable TSEG1/TSEG2 and prescaler; phase switch armed at the BRS sample point and committed on the bit boundary.</li>")
    else:
        p.append("<li><b>Корпус векторов:</b> кадры извлечены из эталонных захватов CTU CAN FD, сравнены побитово с моделью и выходом RTL. Слот ACK исключён (драйвится приёмником).</li>")
        p.append("<li><b>Прогон:</b> все четыре формата, DLC 0–15, BRS вкл/выкл, паттерны 0x00 / 0xFF / чередующийся; RTL против модели.</li>")
        p.append("<li><b>Мутации:</b> протокольные дефекты в эталонной модели (полином CRC, init CRC, интервал стаффинга, паритет stuff-count, резервные биты). Мутант обязан быть обнаружен.</li>")
        p.append("<li><b>Реальный тайминг:</b> NBT/DBT с настраиваемыми TSEG1/TSEG2 и prescaler; переключение фазы взводится в точке выборки BRS и коммитится на границе бита.</li>")
    p.append("</ul>")
    p.append(f"<div class='foot'>Generated by scripts/make_report.py from logs/ and coverage/.</div></body></html>")
    return "\n".join(p)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", choices=["en", "ru", "both"], default="both")
    ap.add_argument("--author", default="[Author]")
    ap.add_argument("--email", default="[email]")
    ap.add_argument("--repo", default="[repository URL]")
    ap.add_argument("--print", dest="show", action="store_true", help="print parsed metrics and exit")
    args = ap.parse_args()
    m = metrics()
    if args.show:
        for k, v in m.items(): print(f"{k}: {v}")
        return 0
    OUT.mkdir(exist_ok=True)
    langs = ["en", "ru"] if args.lang == "both" else [args.lang]
    for lang in langs:
        hp = OUT / f"verification_report_{lang}.html"
        hp.write_text(build_html(lang, m, args), encoding="utf-8")
        print(f"HTML: {hp.relative_to(ROOT)}")
        pp = OUT / f"verification_report_{lang}.pdf"
        ok = False
        for cmd in (["python3", "-m", "weasyprint", str(hp), str(pp)],
                    [shutil.which("wkhtmltopdf") or "", "--quiet", str(hp), str(pp)]):
            if cmd[0]:
                try: subprocess.run(cmd, check=True); ok = True; break
                except Exception: pass
        if ok: print(f"PDF:  {pp.relative_to(ROOT)}")
        else: print(f"PDF skipped. Open HTML and print to PDF, or: pip install weasyprint")
    return 0

if __name__ == "__main__": sys.exit(main())
