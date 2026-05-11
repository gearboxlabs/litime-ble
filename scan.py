import asyncio
from bleak import BleakScanner

async def main():
    devices = await BleakScanner.discover(return_adv=True)

    for address, (device, adv) in devices.items():
        print(f"Address: {address}")
        print(f"Name: {device.name}")
        print(f"RSSI: {adv.rssi}")
        print(f"Metadata: {adv}")
        print("-" * 40)

asyncio.run(main())
