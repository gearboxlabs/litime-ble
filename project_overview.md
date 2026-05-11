# LiTime Bluetooth Battery Protocol Documentation (Initial Reverse Engineering Notes)

## Project Goals

This project aims to:

1. Reverse engineer and document the Bluetooth Low Energy (BLE) protocol used by LiTime smart batteries.
2. Build open-source tooling for reading and monitoring battery telemetry.
3. Integrate LiTime batteries into external ecosystems such as Victron Venus OS / Cerbo GX.
4. Provide long-term interoperability and telemetry access independent of vendor software quality.

---

# Legal / Project Position

This project is intended as an interoperability implementation.

The implementation is based on:

- observation of BLE traffic
- inspection of publicly accessible browser-based implementations
- independent protocol analysis
- independently written software

The project does NOT:

- redistribute vendor firmware
- redistribute proprietary application binaries
- claim affiliation with LiTime
- attempt firmware modification or security bypassing

Recommended branding language:

- "Compatible with LiTime smart batteries"
- Avoid use of official logos or claims of official partnership.

---

# Known Tested Hardware

## Battery

- LiTime 230Ah Smart Bluetooth LiFePO4 Battery
- Serial number:

```text
BDLY12230-bnn-b730171Z-150R
```

## BLE Device Name

Observed advertisement:

```text
L-12230BNN150-B00756
```

## Host Platform

- Apple macOS Tahoe 26.3
- Python 3.9+
- Bleak BLE library

---

# BLE Discovery

## BLE Advertisement

Observed advertisement data:

```text
Service UUID:
0000ffe0-0000-1000-8000-00805f9b34fb
```

## Device Information Service

Observed device information:

| Field | Value |
|---|---|
| Manufacturer | BEKEN SAS |
| Model | BK-BLE-1.0 |
| Firmware | 6.1.2 |
| Software | 6.3.0 |

Note:

The "BEKEN" identifiers appear to refer to the BLE module vendor rather than the BMS manufacturer.

---

# GATT Layout

## Primary Telemetry Service

### Service UUID

```text
0000ffe0-0000-1000-8000-00805f9b34fb
```

### Characteristics

| UUID | Properties | Purpose |
|---|---|---|
| FFE1 | notify/write | Telemetry receive channel |
| FFE2 | write | Command transmit channel |
| FFE3 | notify/write | Unknown / control channel |

Additional custom services exist but have not yet been fully characterized.

---

# Working BLE Communication

## Command Channel

Write commands to:

```text
0000ffe2-0000-1000-8000-00805f9b34fb
```

## Notification Channel

Subscribe to notifications from:

```text
0000ffe1-0000-1000-8000-00805f9b34fb
```

---

# Working Telemetry Request

## Command

Known working telemetry request:

```hex
00 00 04 01 13 55 aa 17
```

This command returns a 105-byte telemetry payload.

---

# Example Telemetry Packet

## Raw Packet

```hex
00 00 65 01 93 55 aa 00 1b 33 00 00 60 33 00 00
d8 0c d8 0c d8 0c d8 0c 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 15 00 15 00 00 00 00 00 00 00 2e 3c 56 5e
00 00 00 00 01 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 3f 00 69 00 00 00 01 00
00 00 06 01 00 00 62
```

---

# Known Packet Offsets

The following offsets are currently confirmed against multiple batteries and validated against values displayed in the official LiTime application.

All integer values are little-endian unless otherwise noted.


## Overall Packet

| Offset | Length | Meaning | Notes |
|---|---|---|---|
| 0-6 | 7 | Packet header | Contains packet metadata |
| 2 | 1 | Payload length | Example value: `0x65 = 101` payload bytes |
| 92-93 | uint16 LE | Packet length field | Observed value: `105` |

---|---|---|---|
| 0-6 | 7 | Packet header | Contains packet metadata |
| 2 | 1 | Payload length | Example value: 0x65 = 101 bytes payload |

---

## Voltage

### Total Pack Voltage

| Offset | Type | Units |
|---|---|---|
| 12-15 | uint32 LE | millivolts |

Example:

```text
0x00003360 = 13152 mV = 13.152 V
```

---

## Cell Voltages

| Offset | Type | Units |
|---|---|---|
| 16-47 | uint16 LE array | millivolts |

Observed:

```text
3.288 V
3.288 V
3.288 V
3.288 V
```

Unused cell entries are zero-filled.

---

## Current

| Offset | Type | Units |
|---|---|---|
| 48-51 | int32 LE | milliamps |

Example:

```text
0 mA = idle
```

---

## Temperature

### Battery Temperature

| Offset | Type | Units |
|---|---|---|
| 52-53 | int16 LE | Celsius |

### MOSFET Temperature

| Offset | Type | Units |
|---|---|---|
| 54-55 | int16 LE | Celsius |

Observed:

```text
21 C
```

---

## Capacity

### Remaining Capacity

| Offset | Type | Units |
|---|---|---|
| 62-63 | uint16 LE | 0.01 Ah |

Example:

```text
15406 = 154.06 Ah
```

### Full Capacity

| Offset | Type | Units |
|---|---|---|
| 64-65 | uint16 LE | 0.01 Ah |

Example:

```text
24150 = 241.50 Ah
```

Observed batteries show that the BMS reports real measured capacity rather than strictly nominal marketed capacity.

Example:

```text
Nominal battery: 230Ah
Reported full capacity: 241.50Ah
```


---

## State of Charge (SOC)

### Reported SOC

| Offset | Type | Units |
|---|---|---|
| 90-91 | uint16 LE | percent |

Observed examples:

| Battery | Raw Value | Displayed SOC |
|---|---:|---:|
| 230Ah battery | 63 | 63% |
| 100Ah battery | 100 | 100% |
| LT-12100BG | 100 | 100% |

This field matches the official LiTime application.

### Calculated SOC

SOC can also be independently calculated from:

```text
remaining_ah / full_capacity_ah
```

This has proven useful as a validation/sanity-check mechanism.


---

## Cycle Count

| Offset | Type | Units |
|---|---|---|
| 96-97 | uint16 LE | cycles |

Observed examples:

| Battery | Raw Value | Cycles Reported By App |
|---|---:|---:|
| 230Ah battery | 1 | 1 |
| 100Ah battery A00433 | 7 | 7 |
| LT-12100BG | 9 | 9 |

This field has been confirmed against values displayed in the official LiTime application.

---

## Unknown Fields

The following fields remain unidentified but are being tracked for future analysis.

| Offset | Type | Notes |
|---|---|---|
| 8-11 | uint32 LE | Appears dynamic |
| 66-69 | uint32 LE | Often zero |
| 70-71 | uint16 LE | Sometimes `0x0001` or `0x0004` |
| 94-95 | uint16 LE | Often zero |
| 98-99 | uint16 LE | Often zero |
| 100-101 | uint16 LE | Unknown configuration/build value |
| 104 | uint8 | Likely checksum or tail byte |

Observed examples for offset 100-101:

| Battery | Value |
|---|---:|
| 230Ah battery | 262 |
| 100Ah battery A00433 | 733 |
| LT-12100BG | 962 |

This field is NOT cycle count.

---

# Multi-Battery Support

The current Python tooling supports:

- automatic BLE scanning
- automatic LiTime battery identification
- simultaneous polling of multiple visible batteries
- human-readable output
- JSON-lines output for machine ingestion
- raw packet capture mode for reverse engineering

Tested successfully with three simultaneous batteries.

---

# Output Modes

## Human-readable Mode

```bash
python litime_reader.py
```

## JSON Lines Mode

```bash
python litime_reader.py --output json
```

Each line contains one complete battery state object.

## Raw Packet Analysis Mode

```bash
python litime_reader.py --output rawjson
```

This mode includes:

- raw packet hex
- decoded fields
- unknown field tracking
- packet metadata

Useful for reverse engineering and protocol analysis.

---

# Derived Metrics

The tooling currently derives several additional metrics.

## Power

```text
watts = voltage * current
```

## Cell Delta

The tooling calculates:

- minimum cell voltage
- maximum cell voltage
- cell voltage delta in volts and millivolts

Example:

```text
Cell min/max: 3.445V / 3.457V
Cell delta:   13mV
```

This is useful for:

- balance monitoring
- identifying weak cells
- evaluating top-of-charge balancing behavior

---

# Python Reference Implementation

## Dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install bleak
```

---

## Working Reader Example

```python
import asyncio
from bleak import BleakClient

ADDRESS = "BLE_DEVICE_ADDRESS"

WRITE_CHAR = "0000ffe2-0000-1000-8000-00805f9b34fb"
NOTIFY_CHAR = "0000ffe1-0000-1000-8000-00805f9b34fb"

COMMAND = bytes.fromhex("00 00 04 01 13 55 aa 17")


def parse(data):
    if len(data) < 100:
        return

    voltage = int.from_bytes(data[12:16], "little") / 1000
    current = int.from_bytes(data[48:52], "little", signed=True) / 1000

    print(voltage, current)


async def main():
    async with BleakClient(ADDRESS) as client:
        await client.start_notify(
            NOTIFY_CHAR,
            lambda sender, data: parse(data)
        )

        while True:
            await client.write_gatt_char(
                WRITE_CHAR,
                COMMAND,
                response=False
            )
            await asyncio.sleep(5)


asyncio.run(main())
```

---

# Current Understanding

The battery appears to implement:

- a custom BLE telemetry protocol
- UART-style BLE transport over FFE0/FFE1/FFE2
- periodic polling request/response telemetry

The protocol does NOT appear to be directly compatible with:

- standard DALY protocol
- standard JBD/Xiaoxiang protocol

although some structural similarities may exist.

---

# Planned Future Work

## Protocol Reverse Engineering

- identify additional packet types
- identify alarm/status bits
- identify cycle count offset
- identify balancing state bits
- identify charge/discharge enable state
- identify protection/fault fields

## Software Development

- stable Python telemetry daemon
- MQTT bridge
- Victron dbus integration
- Venus OS integration package
- Home Assistant integration
- iOS Swift application
- historical telemetry database
- battery fleet monitoring

## Advanced Goals

- multi-battery aggregation
- series/parallel pack abstraction
- estimated runtime calculations
- long-term health analytics
- balancing analysis
- charge/discharge trend analysis
- adaptive polling
- local web dashboard

---

# Safety Notes

This project currently focuses on telemetry READ access only.

Write/configuration operations should be treated cautiously.

Potential risks include:

- modifying BMS protection thresholds
- disabling protections
- damaging battery hardware
- unsafe charging/discharging conditions

No configuration write commands are currently documented.

