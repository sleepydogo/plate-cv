"""
Interfaces de entrada al sistema (CLI, API, etc.).
"""

from .cli import main, detect_command, extract_digits_command

__all__ = ["main", "detect_command", "extract_digits_command"]
