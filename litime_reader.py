#!/usr/bin/env python3

import argparse
import asyncio
import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Dict, List, Optional

from bleak import BleakClient, BleakScanner


LITIME_NAME_RE = re.compile(r"^L-\w+", re.IGNORECASE)
LITIME_SERVICE_UUID = "0000ffe0-0000-1000-8000-00805f9b34fb"

WRITE_CHAR = "0000ffe2-0000-1000-8000-00805f9b34fb"
NOTIFY_CHAR = "0000ffe1-0000-1000-8000-00805f9b34fb"

COMMAND = bytes.fromhex("00 00 04 01 13 55 aa 17")


@dataclass
class LiTimeBattery:
    address: str
    name: str
    rssi: Optional[int]


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


def is_litime_battery(name: Optional[str], service_uuids: List[str]) -> bool:
    if name and LITIME_NAME_RE.match(name):
        return True

    return LITIME_SERVICE_UUID in [uuid.lower() for uuid in service_uuids]


async def scan_litime_batteries(timeout: float) -> List[LiTimeBattery]:
    results = await BleakScanner.discover(timeout=timeout, return_adv=True)
    batteries: List[LiTimeBattery] = []

    for address, (device, adv) in results.items():
        name = device.name or adv.local_name
        service_uuids = [uuid.lower() for uuid in adv.service_uuids]

        if is_litime_battery(name, service_uuids):
            batteries.append(
                LiTimeBattery(
                    address=address,
                    name=name or "Unknown LiTime Battery",
                    rssi=adv.rssi,
                )
            )

    batteries.sort(
        key=lambda b: b.rssi if b.rssi is not None else -999,
        reverse=True,
    )
    return batteries


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

def packet_hex(data: bytearray) -> str:
    return data.hex(" ")


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

        # Still unknown / worth tracking
        "unknown_8_11_u32_le": int.from_bytes(data[8:12], "little"),
        "unknown_66_69_u32_le": int.from_bytes(data[66:70], "little"),
        "unknown_70_71_u16_le": int.from_bytes(data[70:72], "little"),
        "unknown_72_87_hex": data[72:88].hex(" "),
        "unknown_94_95_u16_le": int.from_bytes(data[94:96], "little"),
        "unknown_98_99_u16_le": int.from_bytes(data[98:100], "little"),
        "unknown_100_101_u16_le": int.from_bytes(data[100:102], "little"),
        "checksum_or_tail": data[-1],
    }



def print_human(state: BatteryState) -> None:
    print()
    print(f"=== {state.name} | {state.address} | RSSI {state.rssi} ===")
    print(f"Timestamp:     {state.timestamp}")
    print(f"Voltage:       {state.voltage_v:.3f} V")
    print(f"Current:       {state.current_a:.3f} A")
    print(f"Power:         {state.power_w:.1f} W")
    print(f"Battery temp:  {state.battery_temp_c} C")
    print(f"MOSFET temp:   {state.mosfet_temp_c} C")
    print(f"Remaining:     {state.remaining_ah:.2f} Ah")
    print(f"Full capacity: {state.full_capacity_ah:.2f} Ah")
    print(f"SOC:           {state.soc_percent}%")
    print(f"Cells:         {', '.join(f'{v:.3f} V' for v in state.cell_voltages_v)}")
    if state.cell_voltage_delta_v is not None:
        print(f"Cell min/max:  {state.min_cell_voltage_v:.3f} V / {state.max_cell_voltage_v:.3f} V")
        print(f"Cell delta:    {state.cell_voltage_delta_mv} mV")
    print(f"Cycles:        {state.cycle_count}")

def print_json(state: BatteryState) -> None:
    print(json.dumps(asdict(state), separators=(",", ":")), flush=True)


def emit_state(state, output: str) -> None:
    if output == "json":
        print_json(state)
    elif output == "rawjson":
        print(json.dumps(state, separators=(",", ":")), flush=True)
    else:
        print_human(state)


async def poll_battery(
    battery: LiTimeBattery,
    interval: float,
    output: str,
) -> None:
    while True:
        try:
            if output == "human":
                print(f"Connecting to {battery.name} at {battery.address}")

            async with BleakClient(battery.address) as client:
                if output == "human":
                    print(f"Connected: {battery.name}")

                def notification_handler(sender, data):
                    if output == "rawjson":
                        debug = parse_debug_packet(battery, data)
                        if debug:
                            emit_state(debug, output)
                        return

                    state = parse_packet(battery, data)
                    if state:
                        emit_state(state, output)

                await client.start_notify(NOTIFY_CHAR, notification_handler)

                while client.is_connected:
                    await client.write_gatt_char(
                        WRITE_CHAR,
                        COMMAND,
                        response=False,
                    )
                    await asyncio.sleep(interval)

        except Exception as e:
            if output == "human":
                print(f"Error reading {battery.name}: {e}")
                print(f"Retrying {battery.name} in 10 seconds...")
            await asyncio.sleep(10)


async def main_async(args) -> None:
    batteries = await scan_litime_batteries(timeout=args.scan_timeout)

    if not batteries:
        if args.output == "human":
            print("No likely LiTime batteries found.")
        return

    if args.output == "human":
        print(f"Found {len(batteries)} likely LiTime battery/batteries:")
        for i, battery in enumerate(batteries, start=1):
            print(f"{i}. {battery.name} | {battery.address} | RSSI {battery.rssi}")

    if args.once:
        states: Dict[str, BatteryState] = {}

        async def one_packet(battery: LiTimeBattery) -> None:
            async with BleakClient(battery.address) as client:
                done = asyncio.Event()

                def handler(sender, data):
                    state = parse_packet(battery, data)
                    if state:
                        states[battery.address] = state
                        done.set()

                await client.start_notify(NOTIFY_CHAR, handler)
                await client.write_gatt_char(WRITE_CHAR, COMMAND, response=False)
                await asyncio.wait_for(done.wait(), timeout=args.read_timeout)

        await asyncio.gather(*(one_packet(battery) for battery in batteries))

        for battery in batteries:
            state = states.get(battery.address)
            if state:
                emit_state(state, args.output)

        return

    tasks = [
        asyncio.create_task(
            poll_battery(
                battery=battery,
                interval=args.interval,
                output=args.output,
            )
        )
        for battery in batteries
    ]

    await asyncio.gather(*tasks)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Read telemetry from visible LiTime Bluetooth batteries."
    )

    parser.add_argument(
        "--output",
        choices=["human", "json", "rawjson"],
        default="human",
        help="Output format. Use json for parsed rows, rawjson for packet analysis.",
    )

    parser.add_argument(
        "--interval",
        type=float,
        default=5.0,
        help="Polling interval in seconds.",
    )

    parser.add_argument(
        "--scan-timeout",
        type=float,
        default=10.0,
        help="BLE scan timeout in seconds.",
    )

    parser.add_argument(
        "--read-timeout",
        type=float,
        default=10.0,
        help="Timeout for one-shot reads.",
    )

    parser.add_argument(
        "--once",
        action="store_true",
        help="Read one state from each visible battery and exit.",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()
    asyncio.run(main_async(args))


if __name__ == "__main__":
    main()


