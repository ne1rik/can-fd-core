#!/usr/bin/env python3
"""Добавляет синтетические CRC-21 кадры в корпус, если их там нет.
Запускать ПОСЛЕ xval_ctu_extract_all.py, так как тот перезаписывает файл.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VEC_PATH = ROOT / "coverage" / "ctu_vectors_all.json"

def main():
    if not VEC_PATH.exists():
        print("SKIP: ctu_vectors_all.json not found")
        return 0
    
    with open(VEC_PATH, 'r') as f:
        vectors = json.load(f)
    
    # Проверяем, есть ли уже синтетические CRC-21 кадры
    has_crc21 = any(v.get("frame_format") == 1 and v.get("brs") == 0 and v.get("dlc", 0) >= 11 and v.get("synthetic") for v in vectors)
    
    if has_crc21:
        print("OK: Synthetic CRC-21 frames already present")
        return 0
    
    print("Adding synthetic CRC-21 frames...")
    for dlc in [11, 12, 13, 14, 15]:
        n_bytes = {11: 20, 12: 24, 13: 32, 14: 48, 15: 64}[dlc]
        for pattern, name in [("zeros", [0]*n_bytes), ("ones", [0xFF]*n_bytes), ("alt", [0xAA if i%2==0 else 0x55 for i in range(n_bytes)])]:
            vectors.append({
                "format": "fd_base", "frame_format": 1, "ident_type": 0,
                "rtr": 0, "brs": 0, "esi": 0, "erf": 0, "dlc": dlc,
                "id": 0x16b, "data": name, "synthetic": True
            })
    
    with open(VEC_PATH, 'w') as f:
        json.dump(vectors, f, indent=1)
    print(f"OK: Added synthetic frames. Total vectors: {len(vectors)}")
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
