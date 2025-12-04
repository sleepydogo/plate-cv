"""
Entidades de dominio del sistema de detección de patentes.
"""

from dataclasses import dataclass
from typing import List, Optional, Tuple
import numpy as np


@dataclass
class BoundingBox:
    """Representa un cuadro delimitador rectangular."""

    x: int
    y: int
    width: int
    height: int

    @property
    def area(self) -> int:
        """Calcula el área del cuadro delimitador."""
        return self.width * self.height

    @property
    def aspect_ratio(self) -> float:
        """Calcula la relación de aspecto (ancho/alto)."""
        return self.width / self.height if self.height != 0 else 0

    @property
    def coordinates(self) -> Tuple[int, int, int, int]:
        """Retorna las coordenadas (x, y, x+w, y+h)."""
        return (self.x, self.y, self.x + self.width, self.y + self.height)

    def contains_point(self, x: int, y: int) -> bool:
        """Verifica si un punto está dentro del bounding box."""
        return (self.x <= x <= self.x + self.width and
                self.y <= y <= self.y + self.height)


@dataclass
class DigitRegion:
    """Representa una región que contiene un dígito individual."""

    bounding_box: BoundingBox
    image_data: Optional[np.ndarray] = None
    confidence: float = 0.0
    recognized_digit: Optional[str] = None

    def extract_roi(self, source_image: np.ndarray) -> np.ndarray:
        """Extrae la región de interés de la imagen fuente."""
        bb = self.bounding_box
        return source_image[bb.y:bb.y + bb.height, bb.x:bb.x + bb.width].copy()


@dataclass
class PlateRegion:
    """Representa una región candidata de patente detectada."""

    bounding_box: BoundingBox
    confidence: float
    transitions_count: int
    image_data: Optional[np.ndarray] = None
    digits: List[DigitRegion] = None

    def __post_init__(self):
        if self.digits is None:
            self.digits = []

    @property
    def is_valid(self) -> bool:
        """Verifica si la región es válida según criterios básicos."""
        return self.confidence > 0.5

    def add_digit(self, digit: DigitRegion) -> None:
        """Agrega un dígito detectado a la patente."""
        self.digits.append(digit)

    def get_normalized_transition_value(self) -> float:
        """Obtiene el valor normalizado de transiciones."""
        return self.transitions_count / (self.bounding_box.width + 1)


@dataclass
class DetectionResult:
    """Resultado completo de la detección de patentes."""

    original_image: np.ndarray
    processed_image: Optional[np.ndarray]
    detected_plates: List[PlateRegion]
    processing_time: float = 0.0
    success: bool = False
    error_message: Optional[str] = None

    def __post_init__(self):
        self.success = len(self.detected_plates) > 0 and self.error_message is None

    @property
    def plate_count(self) -> int:
        """Retorna el número de patentes detectadas."""
        return len(self.detected_plates)

    def get_best_plate(self) -> Optional[PlateRegion]:
        """Retorna la patente con mayor confianza."""
        if not self.detected_plates:
            return None
        return max(self.detected_plates, key=lambda p: p.confidence)

    def get_all_bounding_boxes(self) -> List[BoundingBox]:
        """Retorna todos los bounding boxes detectados."""
        return [plate.bounding_box for plate in self.detected_plates]
