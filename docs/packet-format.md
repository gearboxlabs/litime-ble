# Packet Format Documentation

## Example Telemetry Packet

### Raw Packet

```hex
00 00 65 01 93 55 aa 00 1b 33 00 00 60 33 00 00
d8 0c d8 0c d8 0c d8 0c 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 15 00 15 00 00 00 00 00 00 00 2e 3c 56 5e
00 00 00 00 01 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 3f 00 69 00 00 00 01 00
00 00 06 01 00 00 62
```

## Known Packet Offsets

The following offsets are currently confirmed against multiple batteries and validated against values displayed in the official LiTime application.

All integer values are little-endian unless otherwise noted.

### Overall Packet

| Offset | Length | Meaning | Notes |
|---|---|---|---|
| 0-6 | 7 | Packet header | Contains packet metadata |
| 2 | 1 | Payload length | Example value: `0x65 = 101` payload bytes |
| 92-93 | uint16 LE | Packet length field | Observed value: `105` |

### Voltage

#### Total Pack Voltage

| Offset | Type | Units |
|---|---|---|
| 12-15 | uint32 LE | millivolts |

Example:

```text
0x00003360 = 13152 mV = 13.152 V
```

#### Cell Voltages

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