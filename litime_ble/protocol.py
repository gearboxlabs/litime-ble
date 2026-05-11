from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from .scanner import LiTimeBattery


@dataclass
class BatteryState:
    timestamp: str
    name: str
    address: str
    rssi: Optional[int]
    voltage_v: float
    current_a: float
    power_w: float
    battery_temp_c: int
    mosfet_temp_c: int
    remaining_ah: float
    full_capacity_ah: float
    soc_percent: int
    cell_voltages_v: List[float]
    min_cell_voltage_v: Optional[float]
    max_cell_voltage_v: Optional[float]
    cell_voltage_delta_v: Optional[float]
    cell_voltage_delta_mv: Optional[int]
    cycle_count: int


def parse_packet(battery: LiTimeBattery, data: bytearray) -> Optional[BatteryState]:
    if len(data) < 100:
        return None

    voltage = int.from_bytes(data[12:16], "little") / 1000
    current = int.from_bytes(data[48:52], "little", signed=True) / 1000
    power = voltage * current

    battery_temp = int.from_bytes(data[52:54], "little", signed=True)
    mosfet_temp = int.from_bytes(data[54:56], "little", signed=True)

    remaining_ah = int.from_bytes(data[62:64], "little") / 100
    full_capacity_ah = int.from_bytes(data[64:66], "little") / 100

    soc = int.from_bytes(data[90:92], "little")
    cycle_count = int.from_bytes(data[96:98], "little")

    cells: List[float] = []
    for i in range(16, 48, 2):
        mv = int.from_bytes(data[i:i + 2], "little")
        if mv:
            cells.append(mv / 1000)

    if cells:
        min_cell_voltage = min(cells)
        max_cell_voltage = max(cells)
        cell_voltage_delta = max_cell_voltage - min_cell_voltage
        cell_voltage_delta_mv = round(cell_voltage_delta * 1000)
    else:
        min_cell_voltage = None
        max_cell_voltage = None
        cell_voltage_delta = None
        cell_voltage_delta_mv = None

    return BatteryState(
        timestamp=datetime.now().isoformat(timespec="seconds"),
        name=battery.name,
        address=battery.address,
        rssi=battery.rssi,
        voltage_v=voltage,
        current_a=current,
        power_w=power,
        battery_temp_c=battery_temp,
        mosfet_temp_c=mosfet_temp,
        remaining_ah=remaining_ah,
        full_capacity_ah=full_capacity_ah,
        soc_percent=soc,
        cell_voltages_v=cells,
        min_cell_voltage_v=min_cell_voltage,
        max_cell_voltage_v=max_cell_voltage,
        cell_voltage_delta_v=cell_voltage_delta,
        cell_voltage_delta_mv=cell_voltage_delta_mv,
        cycle_count=cycle_count,
    )


def parse_debug_packet(battery: LiTimeBattery, data: bytearray) -> Optional[dict]:
    if len(data) < 100:
        return None

    voltage = int.from_bytes(data[12:16], "little") / 1000
    current = int.from_bytes(data[48:52], "little", signed=True) / 1000
    remaining_ah = int.from_bytes(data[62:64], "little") / 100
    full_capacity_ah = int.from_bytes(data[64:66], "little") / 100

    calculated_soc = (
        (remaining_ah / full_capacity_ah) * 100
        if full_capacity_ah > 0
        else None
    )

    reported_soc = int.from_bytes(data[90:92], "little")
    packet_length_field = int.from_bytes(data[92:94], "little")
    cycle_count = int.from_bytes(data[96:98], "little")

    cells = []
    for i in range(16, 48, 2):
        mv = int.from_bytes(data[i:i + 2], "little")
        if mv:
            cells.append(mv / 1000)

    min_cell = min(cells) if cells else None
    max_cell = max(cells) if cells else None
    cell_delta_v = (max_cell - min_cell) if cells else None
    cell_delta_mv = round(cell_delta_v * 1000) if cell_delta_v is not None else None

    return {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "name": battery.name,
        "address": battery.address,
        "rssi": battery.rssi,
        "packet_len": len(data),
        "packet_length_field": packet_length_field,
        "raw_hex": data.hex(" "),
        "voltage_v": voltage,
        "current_a": current,
        "power_w": voltage * current,
        "battery_temp_c": int.from_bytes(data[52:54], "little", signed=True),
        "mosfet_temp_c": int.from_bytes(data[54:56], "little", signed=True),
        "remaining_ah": remaining_ah,
        "full_capacity_ah": full_capacity_ah,
        "reported_soc_percent": reported_soc,
        "calculated_soc_percent": calculated_soc,
        "cycle_count": cycle_count,
        "cell_voltages_v": cells,
        "min_cell_voltage_v": min_cell,
        "max_cell_voltage_v": max_cell,
        "cell_voltage_delta_v": cell_delta_v,
        "cell_voltage_delta_mv": cell_delta_mv,
        "unknown_8_11_u32_le": int.from_bytes(data[8:12], "little"),
        "unknown_66_69_u32_le": int.from_bytes(data[66:70], "little"),
        "unknown_70_71_u16_le": int.from_bytes(data[70:72], "little"),
        "unknown_72_87_hex": data[72:88].hex(" "),
        "unknown_94_95_u16_le": int.from_bytes(data[94:96], "little"),
        "unknown_98_99_u16_le": int.from_bytes(data[98:100], "little"),
        "unknown_100_101_u16_le": int.from_bytes(data[100:102], "little"),
        "checksum_or_tail": data[-1],
    }
