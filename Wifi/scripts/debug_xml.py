from pathlib import Path

WLAN_EVENTS_INPUT_FILE = Path("data/raw/wlan_events.xml")

raw_bytes = WLAN_EVENTS_INPUT_FILE.read_bytes()

print("=== First 500 bytes (hex) ===")
print(raw_bytes[:500].hex())

print("\n=== First 500 bytes (repr) ===")
print(repr(raw_bytes[:500]))

print("\n=== First 500 chars decoded loosely ===")
print(raw_bytes[:500].decode("utf-8", errors="replace"))