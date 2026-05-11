import asyncio
from bleak import BleakClient

ADDRESS = "3B1DDD32-6904-6FA3-5E45-D243AC65B61A"

NOTIFY_CHARS = [
    "0000ffe1-0000-1000-8000-00805f9b34fb",
    "0000ffe3-0000-1000-8000-00805f9b34fb",
]

WRITE_CHARS = [
    "0000ffe1-0000-1000-8000-00805f9b34fb",
    "0000ffe2-0000-1000-8000-00805f9b34fb",
]

PROBES = [
    ("daly_status", bytes.fromhex("a5 40 90 08 00 00 00 00 00 00 00 00 7d")),
    ("daly_cells",  bytes.fromhex("a5 40 95 08 00 00 00 00 00 00 00 00 82")),
    ("jbd_status",  bytes.fromhex("dd a5 03 00 ff fd 77")),
    ("jbd_cells",   bytes.fromhex("dd a5 04 00 ff fc 77")),
]

def handler(sender, data):
    print(f"NOTIFY {sender}: {data.hex(' ')} | ascii={data!r}")

async def main():
    async with BleakClient(ADDRESS) as client:
        print("Connected:", client.is_connected)

        for char in NOTIFY_CHARS:
            await client.start_notify(char, handler)
            print("Subscribed:", char)

        await asyncio.sleep(1)

        for write_char in WRITE_CHARS:
            for name, probe in PROBES:
                for response in [False, True]:
                    print(f"WRITE {write_char} response={response} {name}: {probe.hex(' ')}")
                    try:
                        await client.write_gatt_char(write_char, probe, response=response)
                    except Exception as e:
                        print("Write failed:", e)
                    await asyncio.sleep(2)

        print("Listening...")
        await asyncio.sleep(10)

asyncio.run(main())


