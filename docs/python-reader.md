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
./bin/litime-reader --battery-name "L-12230XXX-XXXXXXX"
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

# Write one JSON line per battery state to a log file
./bin/litime-reader --battery-name "L-12230XXX-XXXXXXX" --log battery.log

# Log with specific timezone
./bin/litime-reader --battery-name "L-12230XXX-XXXXXXX" --log battery.log --log-timezone America/New_York

# Log with GMT offset
./bin/litime-reader --battery-name "L-12230XXX-XXXXXXX" --log battery.log --log-timezone gmt+5
```

## Logging and Timestamps

The `--log` option writes one JSON line per battery state for easy parsing and archival. Timestamps are configurable with `--log-timezone`:

- **local**: System local timezone (default)
- **utc**: Coordinated Universal Time
- **Named timezones**: IANA timezone names like `America/New_York`, `Europe/London`, `Australia/Sydney`
- **GMT offsets**: Formats like `gmt+5`, `gmt-8` for fixed offsets from UTC

Examples:
```bash
./bin/litime-reader --log data.log
./bin/litime-reader --log data.log --log-timezone utc
./bin/litime-reader --log data.log --log-timezone America/Los_Angeles
./bin/litime-reader --log data.log --log-timezone gmt+9
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