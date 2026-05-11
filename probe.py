import asyncio
from bleak import BleakClient

ADDRESS = "3B1DDD32-6904-6FA3-5E45-D243AC65B61A"

CHARS = [
    "0000ffe1-0000-1000-8000-00805f9b34fb",
    "0000ffe3-0000-1000-8000-00805f9b34fb",
    "f000ffc1-0451-4000-b000-000000000000",
    "f000ffc2-0451-4000-b000-000000000000",
]

# Common DALY-ish / BMS-ish probes
PROBES = [
    bytes.fromhex("a5 40 90 08 00 00 00 00 00 00 00 00 7d"),  # status
    bytes.fromhex("a5 40 91 08 00 00 00 00 00 00 00 00 7e"),  # cell voltages
    bytes.fromhex("a5 40 92 08 00 00 00 00 00 00 00 00 7f"),  # temps
    bytes.fromhex("a5 40 93 08 00 00 00 00 00 00 00 00 80"),  # MOS/status
    bytes.fromhex("dd a5 03 00 ff fd 77"),                    # JBD-style status
    bytes.fromhex("dd a5 04 00 ff fc 77"),                    # JBD-style cell volts
]

def handler(sender, data):
    print(f"NOTIFY {sender}: {data.hex(' ')}")

async def main():
    async with BleakClient(ADDRESS) as client:
        print("Connected:", client.is_connected)

        for char in CHARS:
            try:
                await client.start_notify(char, handler)
                print("Subscribed:", char)
            except Exception as e:
                print("Subscribe failed:", char, e)

        await asyncio.sleep(2)

        for write_char in CHARS:
            for probe in PROBES:
                print(f"WRITE {write_char}: {probe.hex(' ')}")
                try:
                    await client.write_gatt_char(write_char, probe, response=False)
                except Exception as e:
                    print("Write failed:", e)
                await asyncio.sleep(1)

        print("Listening for 10 seconds...")
        await asyncio.sleep(10)

asyncio.run(main())


