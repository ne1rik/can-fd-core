#!/usr/bin/env python3
"""Golden-fixture oracle для CRC-17/21 (mutation testing).
--freeze: PRISTINE-модель фиксирует (crc_width, crc_value) в coverage/crc21_golden.json.
--check : текущая модель пересчитывается; расхождение -> exit 1 (мутация поймана).
Value-level оракул: убивает любое изменение спеки (poly/init/width/stuffing/
stuff-count/gray/parity) в frame_layout. Stream-level мутации остаются за xval.
"""
import hashlib, importlib.util, json, pathlib, sys

ROOT    = pathlib.Path(__file__).resolve().parent.parent
MODEL   = ROOT / "tb" / "can_fd_reference.py"
FIXTURE = ROOT / "coverage" / "crc21_golden.json"

def _pl(dlc, kind):
    n = {11: 20, 12: 24, 13: 32, 14: 48, 15: 64}.get(dlc, dlc if dlc <= 8 else 16)
    if kind == 0: return [0x00] * n
    if kind == 1: return [0xFF] * n
    if kind == 2: return [0x55 if i % 2 == 0 else 0xAA for i in range(n)]
    return list(range(n))

def frames():
    for dlc in (11, 12, 13, 14, 15):        # CRC-21 зона (дыра CTU-корпуса)
        for kind in (0, 1, 2, 3):
            yield 0x16b, dlc, kind
    for dlc in (4, 8, 10):                  # CRC-17 зона (страховка)
        for kind in (0, 1, 2):
            yield 0x16b, dlc, kind

def load_model():
    spec = importlib.util.spec_from_file_location("golden_model", str(MODEL))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

def measure(m):
    res = {}
    for id11, dlc, kind in frames():
        payload = _pl(dlc, kind)
        lay = m.frame_layout(id11, dlc, list(payload), True)   # True = FD (FBFF)
        res["%#05x/%d/%d/%d" % (id11, dlc, kind, len(payload))] = [lay["crc_width"], lay["crc_value"]]
    return res

def freeze():
    md5 = hashlib.md5(MODEL.read_bytes()).hexdigest()
    data = {"model_md5": md5, "frames": measure(load_model())}
    FIXTURE.write_text(json.dumps(data, indent=1, sort_keys=True))
    print("frozen %d frames, model md5=%s -> %s" % (len(data["frames"]), md5, FIXTURE))

def check():
    data = json.loads(FIXTURE.read_text())
    cur = measure(load_model())
    bad = {k: (data["frames"][k], cur.get(k)) for k in data["frames"]
           if data["frames"][k] != cur.get(k)}
    if bad:
        for k, (exp, got) in list(bad.items())[:5]:
            print("MISMATCH %s: golden=%s current=%s" % (k, exp, got))
        print("MISMATCH %d / %d" % (len(bad), len(data["frames"])))
        sys.exit(1)
    print("MATCHED %d / %d  MISMATCH 0" % (len(data["frames"]), len(data["frames"])))
    sys.exit(0)

if __name__ == "__main__":
    (freeze if "--freeze" in sys.argv else check)()
