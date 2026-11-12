def stuff_bits(bitstream: list[int]) -> list[int]:
    stuffed = []
    count = 0
    last_bit = None
    for bit in bitstream:
        stuffed.append(bit)
        if bit == last_bit:
            count += 1
            if count == 5:
                stuffed.append(1 - bit)
                count = 0
                last_bit = 1 - bit
        else:
            count = 1
            last_bit = bit
    return stuffed

def calculate_crc(bitstream: list[int], payload_len_bytes: int) -> list[int]:
    if payload_len_bytes <= 16:
        poly = 0x1685B
        width = 17
    else:
        poly = 0x102899
        width = 21
    
    crc = 0
    for bit in bitstream:
        msb = (crc >> (width - 1)) & 1
        crc = (crc << 1) & ((1 << width) - 1)
        if msb ^ bit:
            crc ^= poly
    
    return [(crc >> i) & 1 for i in range(width - 1, -1, -1)]

def generate_can_fd_frame(id: int, dlc: int, data: list[int], brs: bool = True) -> list[int]:
    raw_bits = [0]  # SOF
    for i in range(10, -1, -1):
        raw_bits.append((id >> i) & 1)
    raw_bits.extend([1, 1, 1, 1 if brs else 0, 0])  # RRS, IDE, FDF, BRS, ESI
    for i in range(3, -1, -1):
        raw_bits.append((dlc >> i) & 1)
    for byte in data:
        for i in range(7, -1, -1):
            raw_bits.append((byte >> i) & 1)
    
    stuffed_bits = stuff_bits(raw_bits)
    crc_bits = calculate_crc(stuffed_bits, len(data))
    
    return stuffed_bits + crc_bits + [1] + [1, 1] + [1]*7

if __name__ == "__main__":
    frame = generate_can_fd_frame(0x123, 9, [0xAA, 0xBB, 0xCC, 0xDD, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88])
    print(f"Длина кадра: {len(frame)} бит")
