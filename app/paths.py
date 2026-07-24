"""Filesystem locations, aware of frozen (PyInstaller) binaries.

- Source checkout: data/ and feeds*.json live next to the repo root.
- Frozen binary: bundled read-only files (feeds.json, feeds_world.json) are
  unpacked into sys._MEIPASS; the WRITABLE data dir defaults to ./data next
  to wherever the binary is run from.
- TRANSIT_DATA_DIR overrides the data dir in both modes.
"""

from __future__ import annotations

import os
import sys

_FROZEN = getattr(sys, "frozen", False)

if _FROZEN:  # pragma: no cover — exercised only inside built binaries
    BUNDLE_DIR = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
    _DEFAULT_DATA = os.path.join(os.getcwd(), "data")
else:
    BUNDLE_DIR = os.path.join(os.path.dirname(__file__), "..")
    _DEFAULT_DATA = os.path.join(BUNDLE_DIR, "data")

DATA_DIR = os.environ.get("TRANSIT_DATA_DIR") or _DEFAULT_DATA


def registry_file(name: str) -> str:
    """Path of feeds.json / feeds_world.json (read-only, bundled when frozen)."""
    return os.path.join(BUNDLE_DIR, name)
