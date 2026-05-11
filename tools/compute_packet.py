from pathlib import Path

hex_blocks = [
    "00 00 65 01 93 55 aa 00 1b 33 00 00 60 33 00 00",
    "d8 0c d8 0c d8 0c d8 0c 00 00 00 00 00 00 00 00",
    "00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00",
    "00 00 15 00 15 00 00 00 00 00 00 00 2e 3c 56 5e",
    "00 00 00 00 01 00 00 00 00 00 00 00 00 00 00 00",
    "00 00 00 00 00 00 00 00 00 00 3f 00 69 00 00 00 01 00",
    "00 00 06 01 00 00 62",
]
hex_text = " ".join(hex_blocks)
packet_bytes = bytearray.fromhex(hex_text)
print(f"len {len(packet_bytes)}")
print(f"hex {packet_bytes.hex()}")
