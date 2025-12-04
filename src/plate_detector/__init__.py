"""
Plate Detector - Sistema de detección de patentes argentinas
usando procesamiento clásico de imágenes.
"""

__version__ = "1.0.0"
__author__ = "Tom Puliendo"

from .application.plate_detection import PlateDetectionService
from .domain.entities import PlateRegion, DetectionResult, BoundingBox

__all__ = [
    "PlateDetectionService",
    "PlateRegion",
    "DetectionResult",
    "BoundingBox",
]
