import json
import unittest
from pathlib import Path

from litime_ble.protocol import parse_debug_packet, parse_packet
from litime_ble.scanner import LiTimeBattery


class ProtocolTest(unittest.TestCase):
    def setUp(self):
        fixture_path = Path(__file__).parent / "fixtures" / "sample_packet.jsonl"
        record = json.loads(fixture_path.read_text())
        self.data = bytearray.fromhex(record["packet_hex"])
        self.expected = record["expected"]
        self.battery = LiTimeBattery(
            address="AA:BB:CC:DD:EE:FF",
            name="L-12230BNN150-B00756",
            rssi=-60,
            service_uuids=["0000ffe0-0000-1000-8000-00805f9b34fb"],
        )

    def test_parse_packet_values(self):
        state = parse_packet(self.battery, self.data)
        self.assertIsNotNone(state)
        self.assertAlmostEqual(state.voltage_v, self.expected["voltage_v"])
        self.assertAlmostEqual(state.current_a, self.expected["current_a"])
        self.assertEqual(state.battery_temp_c, self.expected["battery_temp_c"])
        self.assertEqual(state.mosfet_temp_c, self.expected["mosfet_temp_c"])
        self.assertAlmostEqual(state.remaining_ah, self.expected["remaining_ah"])
        self.assertAlmostEqual(state.full_capacity_ah, self.expected["full_capacity_ah"])
        self.assertEqual(state.soc_percent, self.expected["soc_percent"])
        self.assertEqual(state.cycle_count, self.expected["cycle_count"])
        self.assertEqual(state.cell_voltages_v, self.expected["cell_voltages_v"])
        self.assertAlmostEqual(state.min_cell_voltage_v, self.expected["min_cell_voltage_v"])
        self.assertAlmostEqual(state.max_cell_voltage_v, self.expected["max_cell_voltage_v"])
        self.assertAlmostEqual(state.cell_voltage_delta_v, self.expected["cell_voltage_delta_v"])
        self.assertEqual(state.cell_voltage_delta_mv, self.expected["cell_voltage_delta_mv"])

    def test_parse_debug_packet_values(self):
        debug = parse_debug_packet(self.battery, self.data)
        self.assertIsNotNone(debug)
        self.assertEqual(debug["packet_len"], self.expected["packet_len"])
        self.assertEqual(debug["packet_length_field"], self.expected["packet_length_field"])
        self.assertEqual(debug["reported_soc_percent"], self.expected["soc_percent"])
        self.assertEqual(debug["cycle_count"], self.expected["cycle_count"])
        self.assertEqual(debug["cell_voltages_v"], self.expected["cell_voltages_v"])
        self.assertAlmostEqual(debug["min_cell_voltage_v"], self.expected["min_cell_voltage_v"])
        self.assertAlmostEqual(debug["max_cell_voltage_v"], self.expected["max_cell_voltage_v"])
        self.assertAlmostEqual(debug["cell_voltage_delta_v"], self.expected["cell_voltage_delta_v"])
        self.assertEqual(debug["cell_voltage_delta_mv"], self.expected["cell_voltage_delta_mv"])


if __name__ == "__main__":
    unittest.main()
