"""Pytest configuration: make sibling test modules importable."""
import sys
from pathlib import Path

# Add tests/ to sys.path so tests can import each other
sys.path.insert(0, str(Path(__file__).parent))
