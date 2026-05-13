"""LiTime BLE battery telemetry package."""

from .cli import main
from .protocol import BatteryState, parse_debug_packet, parse_packet, parse_timezone, get_timestamp
from .scanner import LiTimeBattery, scan_litime_batteries

__all__ = [
    "main",
    "BatteryState",
    "parse_debug_packet",
    "parse_packet",
    "parse_timezone",
    "get_timestamp",
    "LiTimeBattery",
    "scan_litime_batteries",
]
