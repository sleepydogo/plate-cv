"""
Capa de dominio - Contiene las entidades y reglas de negocio del sistema.
"""

from .entities import PlateRegion, DetectionResult, BoundingBox, DigitRegion
from .validators import AspectRatioValidator, AreaValidator, TransitionValidator

__all__ = [
    "PlateRegion",
    "DetectionResult",
    "BoundingBox",
    "DigitRegion",
    "AspectRatioValidator",
    "AreaValidator",
    "TransitionValidator",
]
