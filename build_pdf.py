#!/usr/bin/env python3
"""Build or validate the ZK book project artifacts."""

from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"
KNOWN_SUBCOMMANDS = {"latex", "validate"}

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from zkbook_pdf.cli import main


if __name__ == "__main__":
    argv = sys.argv[1:]
    args = argv if argv and argv[0] in KNOWN_SUBCOMMANDS else ["latex", *argv]
    raise SystemExit(main(args))
