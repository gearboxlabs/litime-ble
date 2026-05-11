import asyncio
import json
from dataclasses import asdict
from typing import Dict

from bleak import BleakClient
from bleak.exc import BleakError

from .protocol import BatteryState, parse_debug_packet, parse_packet
from .scanner import LiTimeBattery, scan_litime_batteries


async def list_batteries(timeout: float) -> None:
    try:
        batteries = await scan_litime_batteries(timeout=timeout)
    except BleakError:
        print(
            "Bluetooth error: make sure Bluetooth is enabled and this program is allowed to use it."
        )
        return

    for battery in batteries:
        print(battery.name)


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

                await client.start_notify("0000ffe1-0000-1000-8000-00805f9b34fb", notification_handler)

                while client.is_connected:
                    await client.write_gatt_char(
                        "0000ffe2-0000-1000-8000-00805f9b34fb",
                        bytes.fromhex("00 00 04 01 13 55 aa 17"),
                        response=False,
                    )
                    await asyncio.sleep(interval)

        except BleakError as e:
            print(
                "Bluetooth error: make sure Bluetooth is enabled and this program is allowed to use it."
            )
            if output == "human":
                print(f"Error reading {battery.name}: {e}")
                print(f"Retrying {battery.name} in 10 seconds...")
            await asyncio.sleep(10)
        except Exception as e:
            if output == "human":
                print(f"Error reading {battery.name}: {e}")
                print(f"Retrying {battery.name} in 10 seconds...")
            await asyncio.sleep(10)


async def main_async(args) -> None:
    try:
        batteries = await scan_litime_batteries(timeout=args.scan_timeout)
    except BleakError as e:
        print(
            "Bluetooth error: make sure Bluetooth is enabled and this program is allowed to use it."
        )
        print(f"Details: {e}")
        return

    if args.address:
        batteries = [b for b in batteries if b.address.lower() == args.address.lower()]

    if args.battery_name:
        substring = args.battery_name.lower()
        batteries = [b for b in batteries if substring in b.name.lower()]

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
            try:
                async with BleakClient(battery.address) as client:
                    done = asyncio.Event()

                    def handler(sender, data):
                        state = parse_packet(battery, data)
                        if state:
                            states[battery.address] = state
                            done.set()

                    await client.start_notify("0000ffe1-0000-1000-8000-00805f9b34fb", handler)
                    await client.write_gatt_char(
                        "0000ffe2-0000-1000-8000-00805f9b34fb",
                        bytes.fromhex("00 00 04 01 13 55 aa 17"),
                        response=False,
                    )
                    await asyncio.wait_for(done.wait(), timeout=args.read_timeout)
            except BleakError as e:
                print(
                    "Bluetooth error: make sure Bluetooth is enabled and this program is allowed to use it."
                )
                print(f"Details: {e}")

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
