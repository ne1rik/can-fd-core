#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "tb"))

from can_fd_reference import _raw_of, stuff_bits, dlc_to_bytes
from scripts.xval_ctu_parser import parse_vhdl_reference_data, filter_can_fd_base_frames, strip_idle, seq_to_bitstream

def main():
    vhd = sys.argv[1]
    frames = filter_can_fd_base_frames(parse_vhdl_reference_data(vhd))
    f = frames[0]
    fr = f['frame']
    n = dlc_to_bytes(fr['dlc'])

    raw = _raw_of(fr['identifier'], fr['dlc'], fr['data'][:n], fr['brs'] == 1)
    stuffed, stuff_pos = stuff_bits(raw)
    ctu = seq_to_bitstream(f['seq'], our_bits=stuffed, brs=fr['brs']==1)

    # Находим начало CRC в "сыром" потоке. Оно после SOF+ID+RRS+IDE+FDF+BRS+ESI+DLC+Data
    crc_start_raw = 1 + 11 + 1 + 1 + 1 + 1 + 1 + 4 + n * 8
    # Находим соответствующую позицию в стаффленном потоке
    crc_start_stuffed = len(stuff_bits(raw[:crc_start_raw])[0])

    print(f"=== Frame 0: ID={fr['identifier']:#x} DLC={fr['dlc']} ===")
    print(f"CRC starts at raw bit {crc_start_raw}, stuffed bit {crc_start_stuffed}")
    print(f"\nStuff positions in first 60 raw bits: {stuff_pos[:10]}")
    print(f"\nOur stuffed bits around CRC (from bit {crc_start_stuffed}):")
    print("  " + ''.join(map(str, stuffed[crc_start_stuffed:crc_start_stuffed+40])))
    print(f"\nCTU bits around same position (from bit {crc_start_stuffed}):")
    print("  " + ''.join(map(str, ctu[crc_start_stuffed:crc_start_stuffed+40])))

if __name__ == "__main__":
    main()
