# Project Summary

This project provides:

- reverse-engineered BLE support for LiTime batteries
- Python telemetry tooling
- multi-battery monitoring
- machine-readable telemetry output

Primary goals:

1. Open-source LiTime BLE interoperability
2. Better telemetry tooling than the official app
3. Local-first battery monitoring
4. Integration into existing power ecosystems

# Multi-Battery Support

The current Python tooling supports:

- automatic BLE scanning
- automatic LiTime battery identification
- simultaneous polling of multiple visible batteries
- human-readable output
- JSON-lines output for machine ingestion
- raw packet capture mode for reverse engineering

Tested successfully with three simultaneous batteries.

# Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 litime_reader.py --help
```



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

# Safety Notes

This project currently focuses on telemetry READ access only.

Write/configuration operations should be treated cautiously.

Potential risks include:

- modifying BMS protection thresholds
- disabling protections
- damaging battery hardware
- unsafe charging/discharging conditions

No configuration write commands are currently documented.

