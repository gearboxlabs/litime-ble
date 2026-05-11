import asyncio
from bleak import BleakClient

ADDRESS = "3B1DDD32-6904-6FA3-5E45-D243AC65B61A"

async def main():
    async with BleakClient(ADDRESS) as client:
        print("Connected:", client.is_connected)

        for service in client.services:
            print(f"\nService: {service.uuid} - {service.description}")
            for char in service.characteristics:
                print(f"  Char: {char.uuid}")
                print(f"    Properties: {char.properties}")
                print(f"    Description: {char.description}")

                if "read" in char.properties:
                    try:
                        value = await client.read_gatt_char(char.uuid)
                        print(f"    Read: {value.hex(' ')}")
                    except Exception as e:
                        print(f"    Read failed: {e}")

asyncio.run(main())


