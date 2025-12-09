#!/usr/bin/env python3
"""
CactUScript - Main Entry Point

A programming language designed for decentralized applications (dApps)
and smart contracts within the Solana ecosystem.

Usage:
    python main.py                    # Start REPL
    python main.py script.cact        # Run a file
    python main.py --help             # Show help
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from cactuscript.cli import main

if __name__ == "__main__":
    main()
