#!/usr/bin/env python3
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tb"))
sys.path.insert(0, str(ROOT / "scripts"))

from can_fd_reference import generate_can_fd_frame, dlc_len
from xval_ctu_wave_diag import tuples, fields, expand

def main():
    path = ROOT.parent / "ctu-can-fd-ref/test/main_tb/reference_test_data_sets/reference_data_set_1.vhd"
    for t in tuples(path.read_text()):
        f, seq = fields(t)
        if f['ff'] == 0 and f['it'] == 0 and f['rtr'] == 0 and f['erf'] == 0 and f['esi'] == 0:
            # Это classic_base
            nb = dlc_len(f['dlc'], classic=True)
            data = (f['data'] + [0] * nb)[:nb]
            ours = generate_can_fd_frame(f['id'], f['dlc'], data, False, extended=False, classic=True)
            ctu = expand(seq)
            
            L = len(ours)
            if len(ctu) < L:
                print(f"SHORT: id={f['id']:#x} dlc={f['dlc']} ours={L} ctu={len(ctu)}")
                return
            pre = L - 9
            if ctu[:pre] != ours[:pre]:
                k = next(i for i, (a, b) in enumerate(zip(ctu[:pre], ours[:pre])) if a != b)
                print(f"MISMATCH at bit {k}")
                print(f"ID: {f['id']:#x}, DLC: {f['dlc']}")
                print(f"ours len: {L}, ctu len: {len(ctu)}")
                print(f"ours[{max(0,k-10):k+15}]: {''.join(map(str, ours[max(0,k-10):k+15]))}")
                print(f"ctu [{max(0,k-10):k+15}]: {''.join(map(str, ctu[max(0,k-10):k+15]))}")
                return
            print("First classic_base frame is a MATCH. The bug is elsewhere in the loop.")
            return

if __name__ == "__main__":
    main()
