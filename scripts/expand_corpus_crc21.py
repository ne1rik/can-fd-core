#!/usr/bin/env python3
"""Permanently adds 15 synthetic CRC-21 frames to close the verification gap."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VEC_PATH = ROOT / "coverage" / "ctu_vectors_all.json"

vectors = json.loads(VEC_PATH.read_text())

# Проверяем, не добавлены ли они уже
has_crc21 = any(v.get("frame_format") == 1 and v.get("brs") == 0 and v.get("dlc", 0) >= 11 for v in vectors)

if has_crc21:
    print("✅ Синтетические CRC-21 кадры уже присутствуют в корпусе.")
else:
    added = 0
    for dlc in [11, 12, 13, 14, 15]:
        n_bytes = {11: 20, 12: 24, 13: 32, 14: 48, 15: 64}[dlc]
        for pattern in ["zeros", "ones", "alt"]:
            if pattern == "zeros":
                data = [0] * n_bytes
            elif pattern == "ones":
                data = [0xFF] * n_bytes
            else:
                data = [0xAA if i % 2 == 0 else 0x55 for i in range(n_bytes)]
            
            vectors.append({
                "format": "fd_base",
                "frame_format": 1,
                "ident_type": 0,
                "rtr": 0,
                "brs": 0,
                "esi": 0,
                "erf": 0,
                "dlc": dlc,
                "id": 0x16b,
                "data": data,
                "synthetic": True  # Явная маркировка
            })
            added += 1
    
    VEC_PATH.write_text(json.dumps(vectors, indent=1))
    print(f"✅ Успешно добавлено {added} синтетических CRC-21 кадров в корпус.")
    print(f"   Новый размер корпуса: {len(vectors)} векторов.")
