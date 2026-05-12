# Victron Integration

## Overview

Integration with Victron Energy's Venus OS platform to enable LiTime batteries in off-grid solar power systems.

## Architecture

### Python Telemetry Daemon

- Stable BLE polling service
- MQTT bridge for data distribution
- dbus integration for Venus OS
- Configuration management
- Error handling and recovery

### Venus OS Package

- dbus service registration
- Battery parameter mapping
- SOC estimation algorithms
- Protection integration
- Historical data logging

## Implementation Plan

### Phase 1: Basic Integration

- Python daemon with BLE connectivity
- MQTT publishing of telemetry data
- Basic Venus OS dbus service
- Manual SOC configuration

### Phase 2: Advanced Features

- Automatic SOC estimation
- Temperature compensation
- Balancing status monitoring
- Fault detection and reporting
- Historical trend analysis

### Phase 3: Fleet Management

- Multi-battery aggregation
- Series/parallel configuration support
- Load balancing algorithms
- Centralized monitoring dashboard

## dbus Interface

The integration will implement Victron's battery dbus interface:

```
/com/victronenergy/battery/litime_XXXX
```

With standard battery parameters:
- Voltage (V)
- Current (A)
- Power (W)
- SOC (%)
- Time to go (seconds)
- Temperature (°C)
- Alarm flags

## MQTT Topics

Telemetry data published to MQTT for external integrations:

```
litime/battery/{serial}/voltage
litime/battery/{serial}/current
litime/battery/{serial}/soc
litime/battery/{serial}/cells/{index}
```

## Configuration

Venus OS configuration file for battery parameters:

```ini
[DEFAULT]
battery_capacity = 230
cell_count = 16
chemistry = LiFePO4
```

## Dependencies

- bleak (BLE library)
- paho-mqtt (MQTT client)
- dbus-python (dbus integration)
- python-systemd (service management)