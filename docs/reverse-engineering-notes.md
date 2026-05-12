# Reverse Engineering Notes

## Analysis Process

This protocol was reverse engineered through:

- Observation of BLE traffic using Wireshark and BLE sniffing tools
- Inspection of publicly accessible browser-based implementations
- Independent protocol analysis
- Correlation with official app displayed values

## Unknown Fields

The following packet fields remain unidentified:

### Protocol Reverse Engineering Goals

- identify additional packet types
- identify alarm/status bits
- identify cycle count offset
- identify balancing state bits
- identify charge/discharge enable state
- identify protection/fault fields

### Current Packet Coverage

The 105-byte telemetry packet contains many fields that appear to be:

- Zero-filled (likely unused/reserved)
- Status bits (alarms, protection states)
- Configuration parameters
- Historical/cycle data
- Temperature readings
- Current measurements

### Packet Structure Notes

- Header appears to contain metadata (length, sequence, type)
- Voltage data is well-confirmed and validated
- Many 16-bit and 32-bit fields remain unmapped
- Some fields may be big-endian (investigation needed)

### Additional Services

The GATT server exposes additional custom services beyond the primary telemetry service (FFE0). These have not been characterized and may contain:

- Configuration commands
- Firmware update capabilities
- Advanced diagnostics
- Calibration data

## Validation Methods

Current validation relies on:

- Correlation with official LiTime app values
- Consistency across multiple batteries
- Physical measurement verification (multimeter)
- Expected value ranges for LiFePO4 chemistry

## Future Analysis

Planned reverse engineering work:

- Capture additional packet types
- Analyze status bit patterns
- Document temperature sensor mappings
- Identify current/power measurement fields
- Map protection and alarm conditions