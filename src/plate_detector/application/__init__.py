"""
Capa de aplicación - Casos de uso del sistema.
"""

from .plate_detection import PlateDetectionService
from .digit_extraction import DigitExtractionService

__all__ = [
    "PlateDetectionService",
    "DigitExtractionService",
]
