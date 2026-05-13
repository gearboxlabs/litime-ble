# GBL LiTime BLE Battery Protocol Documentation

This project provides open-source interoperability with LiTime smart batteries through reverse-engineered Bluetooth Low Energy (BLE) protocol implementation.

**Credits**: This work builds upon the reverse engineering efforts of [chadj/litime-bluetooth-battery](https://github.com/chadj/litime-bluetooth-battery/).

## Overview

- **Protocol**: Custom BLE telemetry protocol over UART-style transport
- **Compatibility**: LiTime 230Ah Smart Bluetooth LiFePO4 Battery (tested)
- **Tooling**: Python CLI for battery monitoring and data export
- **Integrations**: Planned support for Victron Venus OS, Home Assistant, MQTT

## Quick Start

```bash
# Install
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# List batteries
./bin/litime-reader --list-batteries

# Read battery data
./bin/litime-reader --battery-name "L-12230XXX-XXXXXXX"
```

## Documentation Sections

- [Protocol Details](protocol.md) - BLE communication and GATT layout
- [Packet Format](packet-format.md) - Telemetry packet structure and offsets
- [Python Reader](python-reader.md) - CLI usage and API reference
- [Reverse Engineering](reverse-engineering-notes.md) - Analysis process and unknowns
- [Victron Integration](victron-integration.md) - Venus OS integration plans
- [Legal Notes](legal-notes.md) - Project position and disclaimers