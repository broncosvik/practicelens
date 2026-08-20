#!/usr/bin/env python3
"""Backward-compatible CLI entry point and public import facade.

New non-interactive consumers, including the future web application, should
import business logic directly from :mod:`acquisition_engine`.
"""

from acquisition_engine import *  # Re-export the established calculation API.
from practice_cli import *  # Preserve existing CLI/test imports.


if __name__ == "__main__":
    try:
        main()
    except (EOFError, KeyboardInterrupt):
        print("\nCancelled.")
