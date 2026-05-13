from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from typing import List, Optional
from zoneinfo import ZoneInfo

from .scanner import LiTimeBattery


def parse_timezone(tz_spec: Optional[str]) -> Optional[timezone]:
    """Parse timezone specification: 'local' (system timezone), 'utc', named zone (e.g., 'America/New_York'), or offset (e.g., 'gmt+5', 'gmt-8').
    
    Returns None for 'local' to signal that local system timezone should be used.
    """
    if not tz_spec:
        return None

    tz_lower = tz_spec.lower().strip()

    # Local system timezone
    if tz_lower == "local":
        return None

    # UTC
    if tz_lower == "utc":
        return timezone.utc

    # GMT offset: gmt+5, gmt-8, etc.
    if tz_lower.startswith("gmt"):
        try:
            offset_str = tz_lower[3:]
            sign = 1 if offset_str[0] == "+" else -1
            hours = int(offset_str[1:])
            return timezone(timedelta(hours=sign * hours))
        except (ValueError, IndexError):
            raise ValueError(f"Invalid GMT offset format: {tz_spec}")

    # Named timezone
    try:
        return ZoneInfo(tz_spec)
    except Exception:
        raise ValueError(f"Unknown timezone: {tz_spec}")


def get_timestamp(tz: Optional[timezone] = None) -> str:
    """Generate ISO format timestamp.
    
    If tz is None, uses system local timezone (default).
    If tz is a timezone object, uses that timezone.
    """
    if tz is None:
        # Local system timezone
        return datetime.now().astimezone().isoformat(timespec="seconds")
    else:
        return datetime.now(tz).isoformat(timespec="seconds")


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


def parse_packet(battery: LiTimeBattery, data: bytearray, tz: Optional[timezone] = None) -> Optional[BatteryState]:
    if len(data) < 100:
        return None

    voltage = round(int.from_bytes(data[12:16], "little") / 1000, 3)
    current = round(int.from_bytes(data[48:52], "little", signed=True) / 1000, 3)
    power = round(voltage * current, 1)

    battery_temp = int.from_bytes(data[52:54], "little", signed=True)
    mosfet_temp = int.from_bytes(data[54:56], "little", signed=True)

    remaining_ah = round(int.from_bytes(data[62:64], "little") / 100, 2)
    full_capacity_ah = round(int.from_bytes(data[64:66], "little") / 100, 2)

    soc = int.from_bytes(data[90:92], "little")
    cycle_count = int.from_bytes(data[96:98], "little")

    cells: List[float] = []
    for i in range(16, 48, 2):
        mv = int.from_bytes(data[i:i + 2], "little")
        if mv:
            cells.append(round(mv / 1000, 3))

    if cells:
        min_cell_voltage = min(cells)
        max_cell_voltage = max(cells)
        cell_voltage_delta = round(max_cell_voltage - min_cell_voltage, 3)
        cell_voltage_delta_mv = round(cell_voltage_delta * 1000)
    else:
        min_cell_voltage = None
        max_cell_voltage = None
        cell_voltage_delta = None
        cell_voltage_delta_mv = None

    return BatteryState(
        timestamp=get_timestamp(tz),
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


def parse_debug_packet(battery: LiTimeBattery, data: bytearray, tz: Optional[timezone] = None) -> Optional[dict]:
    if len(data) < 100:
        return None

    voltage = round(int.from_bytes(data[12:16], "little") / 1000, 3)
    current = round(int.from_bytes(data[48:52], "little", signed=True) / 1000, 3)
    remaining_ah = round(int.from_bytes(data[62:64], "little") / 100, 2)
    full_capacity_ah = round(int.from_bytes(data[64:66], "little") / 100, 2)

    calculated_soc = (
        round((remaining_ah / full_capacity_ah) * 100, 2)
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
            cells.append(round(mv / 1000, 3))

    min_cell = min(cells) if cells else None
    max_cell = max(cells) if cells else None
    cell_delta_v = round(max_cell - min_cell, 3) if cells else None
    cell_delta_mv = round(cell_delta_v * 1000) if cell_delta_v is not None else None

    return {
        "timestamp": get_timestamp(tz),
        "name": battery.name,
        "address": battery.address,
        "rssi": battery.rssi,
        "packet_len": len(data),
        "packet_length_field": packet_length_field,
        "raw_hex": data.hex(" "),
        "voltage_v": voltage,
        "current_a": current,
        "power_w": round(voltage * current, 1),
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
