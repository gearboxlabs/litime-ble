from pathlib import Path

hex_text = (
    "00 00 65 01 93 55 aa 00 1b 33 00 00 60 33 00 00 "
    "d8 0c d8 0c d8 0c d8 0c 00 00 00 00 00 00 00 00 "
    "00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 "
    "00 00 00 00 2e 3c 56 5e 00 00 00 00 01 00 00 00 "
    "00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 "
    "00 00 00 00 00 00 00 00 3f 00 69 00 00 00 01 00 "
    "00 00 06 01 00 00 62"
)

raw_bytes = bytes.fromhex(hex_text)

fields = {
    "len": len(raw_bytes),
    "packet_length_field": int.from_bytes(raw_bytes[92:94], "little"),
    "voltage": int.from_bytes(raw_bytes[12:16], "little") / 1000.0,
    "current": int.from_bytes(raw_bytes[48:52], "little", signed=True) / 1000.0,
    "battery_temp": int.from_bytes(raw_bytes[52:54], "little", signed=True),
    "mosfet_temp": int.from_bytes(raw_bytes[54:56], "little", signed=True),
    "remaining_ah": int.from_bytes(raw_bytes[62:64], "little") / 100.0,
    "full_capacity_ah": int.from_bytes(raw_bytes[64:66], "little") / 100.0,
    "reported_soc": int.from_bytes(raw_bytes[90:92], "little"),
    "cycle_count": int.from_bytes(raw_bytes[96:98], "little"),
    "cells": [
        int.from_bytes(raw_bytes[i : i + 2], "little")
        for i in range(16, 48, 2)
    ],
}

print(fields)
