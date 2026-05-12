# Project Goals

This project aims to:

1. Reverse engineer and document the Bluetooth Low Energy (BLE) protocol used by LiTime smart batteries.
2. Build open-source tooling for reading and monitoring battery telemetry.
3. Integrate LiTime batteries into external ecosystems such as Victron Venus OS / Cerbo GX.
4. Provide long-term interoperability and telemetry access independent of vendor software quality.

## Future Goals

### Protocol Reverse Engineering

- identify additional packet types
- identify alarm/status bits
- identify cycle count offset
- identify balancing state bits
- identify charge/discharge enable state
- identify protection/fault fields

### Victron Energy Software Development

- stable Python telemetry daemon
- MQTT bridge
- Victron dbus integration
- Venus OS integration package
- Home Assistant integration
- iOS Swift application
- historical telemetry database
- battery fleet monitoring

### Advanced Goals

- multi-battery aggregation
- series/parallel pack abstraction
- estimated runtime calculations
- long-term health analytics
- balancing analysis
- charge/discharge trend analysis
- adaptive polling
- local web dashboard
