from pathlib import Path
import json

fixture_path = Path(__file__).parent.parent / "tests" / "fixtures" / "sample_packet.jsonl"
record = json.loads(fixture_path.read_text())
packet_hex = record["packet_hex"]
packet_bytes = bytearray.fromhex(packet_hex)
print("len", len(packet_bytes))
print("bytes", packet_bytes[:20])
