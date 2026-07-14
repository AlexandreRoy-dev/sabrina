#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parent

replacements = [
    (ROOT / "proprio_sync.py", [
        ("https://melaniefafardimmo.com", "https://vendreavecsabrina.ca"),
        ("https://propriodirect.com/melanie-fafard", "https://propriodirect.com/sabrina-lagasse/"),
        ("Mélanie Fafard", "Sabrina Lagassé"),
        ("melanie-fafard", "sabrina-lagasse"),
    ]),
    (ROOT.parent / ".github" / "workflows" / "proprio-sync.yml", [
        ("https://propriodirect.com/melanie-fafard", "https://propriodirect.com/sabrina-lagasse/"),
    ]),
    (ROOT / "update_map_pins.py", [
        ("MelanieFafard", "SabrinaLagasse"),
        ('"min_lat": 46.2', '"min_lat": 45.0'),
        ('"min_lng": -72.3', '"min_lng": -74.5'),
    ]),
    (ROOT / "README_proprio_sync.md", [
        ("Mélanie Fafard", "Sabrina Lagassé"),
        ("melaniefafardimmo.com", "vendreavecsabrina.ca"),
        ("propriodirect.com/melanie-fafard", "propriodirect.com/sabrina-lagasse/"),
    ]),
]

for path, pairs in replacements:
    text = path.read_text(encoding="utf-8")
    for old, new in pairs:
        text = text.replace(old, new)
    path.write_text(text, encoding="utf-8")
    print("updated", path)
