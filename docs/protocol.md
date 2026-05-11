# LiTime<->BLE Overview

# Current Understanding

The battery appears to implement:

- a custom BLE telemetry protocol
- UART-style BLE transport over FFE0/FFE1/FFE2
- periodic polling request/response telemetry

The protocol does NOT appear to be directly compatible with:

- standard DALY protocol
- standard JBD/Xiaoxiang protocol

although some structural similarities may exist.

# Project Goals

This project aims to:

1. Reverse engineer and document the Bluetooth Low Energy (BLE) protocol used by LiTime smart batteries.
2. Build open-source tooling for reading and monitoring battery telemetry.
3. Integrate LiTime batteries into external ecosystems such as Victron Venus OS / Cerbo GX.
4. Develop an independent iOS application with functionality beyond the official LiTime application.
5. Provide long-term interoperability and telemetry access independent of vendor software quality.


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

