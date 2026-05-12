# Python Reader Documentation

## Installation

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## CLI Usage

### List Available Batteries

```bash
./bin/litime-reader --list-batteries
```

### Read Battery Data

```bash
# By device name
./bin/litime-reader --battery-name "L-12230XXX-XXXXXXX"

# By Bluetooth address
./bin/litime-reader --address "AA:BB:CC:DD:EE:FF"

# Continuous polling (every 30 seconds)
./bin/litime-reader --battery-name "L-12230XXX-XXXXXXX" --poll
```

### Output Formats

The reader supports multiple output formats:

- **Human-readable** (default): Formatted text output
- **JSON**: Machine-readable structured data
- **CSV**: Comma-separated values for logging

```bash
# JSON output
./bin/litime-reader --battery-name "L-12230XXX-XXXXXXX" --format json

# CSV output
./bin/litime-reader --battery-name "L-12230XXX-XXXXXXX" --format csv
```

## API Usage

```python
from litime_ble import BatteryState, poll_battery, list_batteries

# List available batteries
batteries = list_batteries()
print(f"Found batteries: {batteries}")

# Poll specific battery
state = poll_battery("L-12230XXX-XXXXXXX")
print(f"Voltage: {state.total_voltage:.3f}V")
print(f"Cells: {[f'{v:.3f}V' for v in state.cell_voltages]}")
```

## Data Structures

### BatteryState

```python
@dataclass
class BatteryState:
    total_voltage: float      # Total pack voltage in volts
    cell_voltages: List[float]  # Individual cell voltages in volts
    # Additional fields to be documented as reverse engineering progresses
```

## Error Handling

The CLI handles common Bluetooth errors gracefully:

- **Permission denied**: Check Bluetooth permissions
- **Device not found**: Verify battery is powered on and in range
- **Connection timeout**: Retry or check battery status

Use `--help` for complete command-line options.