import re
from dataclasses import dataclass
from typing import List, Optional

from bleak import BleakScanner

LITIME_NAME_RE = re.compile(r"^L-\w+", re.IGNORECASE)
LITIME_SERVICE_UUID = "0000ffe0-0000-1000-8000-00805f9b34fb"


@dataclass
class LiTimeBattery:
    address: str
    name: str
    rssi: Optional[int]
    service_uuids: List[str]


def is_litime_battery(name: Optional[str], service_uuids: List[str]) -> bool:
    if name and LITIME_NAME_RE.match(name):
        return True

    return LITIME_SERVICE_UUID in [uuid.lower() for uuid in service_uuids]


async def scan_litime_batteries(timeout: float = 10.0) -> List[LiTimeBattery]:
    results = await BleakScanner.discover(timeout=timeout, return_adv=True)
    batteries: List[LiTimeBattery] = []

    for address, (device, adv) in results.items():
        name = device.name or adv.local_name
        service_uuids = [uuid.lower() for uuid in (adv.service_uuids or [])]

        if is_litime_battery(name, service_uuids):
            batteries.append(
                LiTimeBattery(
                    address=address,
                    name=name or "Unknown LiTime Battery",
                    rssi=adv.rssi,
                    service_uuids=service_uuids,
                )
            )

    batteries.sort(key=lambda b: b.rssi if b.rssi is not None else -999, reverse=True)
    return batteries


async def main():
    batteries = await scan_litime_batteries()

    if not batteries:
        print("No LiTime batteries found.")
        return

    print(f"Found {len(batteries)} likely LiTime battery/batteries:\n")

    for i, battery in enumerate(batteries, start=1):
        print(f"{i}. {battery.name}")
        print(f"   Address: {battery.address}")
        print(f"   RSSI:    {battery.rssi}")
        print(f"   UUIDs:   {', '.join(battery.service_uuids)}")
        print()
