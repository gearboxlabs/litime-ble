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

fields = {
    "packet_len": len(packet_bytes),
    "packet_length_field": int.from_bytes(packet_bytes[92:94], "little"),
    "voltage_v": int.from_bytes(packet_bytes[12:16], "little") / 1000.0,
    "current_a": int.from_bytes(packet_bytes[48:52], "little", signed=True) / 1000.0,
    "battery_temp_c": int.from_bytes(packet_bytes[52:54], "little", signed=True),
    "mosfet_temp_c": int.from_bytes(packet_bytes[54:56], "little", signed=True),
    "remaining_ah": int.from_bytes(packet_bytes[62:64], "little") / 100.0,
    "full_capacity_ah": int.from_bytes(packet_bytes[64:66], "little") / 100.0,
    "soc_percent": int.from_bytes(packet_bytes[90:92], "little"),
    "cycle_count": int.from_bytes(packet_bytes[96:98], "little"),
    "cells_mv": [int.from_bytes(packet_bytes[i:i+2], "little") for i in range(16, 48, 2)],
}

print(fields)
