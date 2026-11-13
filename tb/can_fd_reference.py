def stuff_bits(bitstream: list[int]) -> tuple[list[int], list[tuple[int, int, int]]]:
    """Применяет бит-стаффинг. Возвращает стаффированный поток и список (raw_idx, stuffed_idx, bit)."""
    out, pos = [], []
    last, run = None, 0
    for i, b in enumerate(bitstream):
        out.append(b)
        if b == last:
            run += 1
        else:
            last, run = b, 1
        if run == 5:
            sb = 1 - b
            out.append(sb)
            pos.append((i, len(out) - 1, sb))
            last, run = sb, 1
    return out, pos

def calculate_crc(bitstream: list[int], payload_len_bytes: int) -> list[int]:
    if payload_len_bytes <= 16:
        poly, width = 0x1685B, 17
    else:
        poly, width = 0x102899, 21
    
    crc = 0
    for bit in bitstream:
        msb = (crc >> (width - 1)) & 1
        crc = (crc << 1) & ((1 << width) - 1)
        if msb ^ bit:
            crc ^= poly
    
    return [(crc >> i) & 1 for i in range(width - 1, -1, -1)]

def generate_can_fd_frame(id: int, dlc: int, data: list[int], brs: bool = True) -> tuple[list[int], int]:
    """
    Генерирует кадр CAN FD и возвращает (bitstream, brs_index).
    brs_index — это индекс бита BRS в УЖЕ стаффированном потоке.
    """
    raw_bits = [0]  # SOF
    for i in range(10, -1, -1):
        raw_bits.append((id >> i) & 1)
    # RRS=1, IDE=1, FDF=1, BRS, ESI=0
    raw_bits.extend([1, 1, 1, 1 if brs else 0, 0])
    for i in range(3, -1, -1):
        raw_bits.append((dlc >> i) & 1)
    for byte in data:
        for i in range(7, -1, -1):
            raw_bits.append((byte >> i) & 1)
    
    stuffed_bits, pos = stuff_bits(raw_bits)
    
    # Считаем, сколько стафф-битов было вставлено ДО бита BRS (raw index 15)
    stuff_before_brs = sum(1 for raw_idx, _, _ in pos if raw_idx < 15)
    brs_index = 15 + stuff_before_brs
    
    crc_bits = calculate_crc(stuffed_bits, len(data))
    
    # CRC Delimiter(1) + ACK(2) + EOF(7)
    final_frame = stuffed_bits + crc_bits + [1, 1, 1] + [1] * 7
    
    return final_frame, brs_index

def dlc_len(d: int) -> int:
    return d if d <= 8 else {9: 12, 10: 16, 11: 20, 12: 24, 13: 32, 14: 48, 15: 64}[d]

if __name__ == "__main__":
    frame, brs_idx = generate_can_fd_frame(0x5AA, 8, [0xFF] * 8, True)
    print(f"Anchor frame length: {len(frame)}, BRS index: {brs_idx}")
