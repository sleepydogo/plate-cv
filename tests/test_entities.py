"""
Tests para las entidades de dominio.
"""

import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from plate_detector.domain.entities import BoundingBox, PlateRegion, DetectionResult
import numpy as np


def test_bounding_box_area():
    """Test del cálculo de área."""
    bb = BoundingBox(x=0, y=0, width=120, height=40)
    assert bb.area == 4800


def test_bounding_box_aspect_ratio():
    """Test del cálculo de relación de aspecto."""
    bb = BoundingBox(x=0, y=0, width=120, height=40)
    assert bb.aspect_ratio == 3.0


def test_bounding_box_contains_point():
    """Test de verificación de punto dentro del bbox."""
    bb = BoundingBox(x=10, y=10, width=50, height=30)
    assert bb.contains_point(20, 20) == True
    assert bb.contains_point(5, 5) == False
    assert bb.contains_point(100, 100) == False


def test_plate_region_normalized_transitions():
    """Test del cálculo de transiciones normalizadas."""
    bb = BoundingBox(x=0, y=0, width=120, height=40)
    plate = PlateRegion(bounding_box=bb, confidence=0.8, transitions_count=450)

    normalized = plate.get_normalized_transition_value()
    expected = 450 / (120 + 1)
    assert abs(normalized - expected) < 0.01


def test_detection_result_success():
    """Test de resultado exitoso."""
    image = np.zeros((480, 640, 3), dtype=np.uint8)
    bb = BoundingBox(x=100, y=50, width=120, height=40)
    plate = PlateRegion(bounding_box=bb, confidence=0.9, transitions_count=500)

    result = DetectionResult(
        original_image=image,
        processed_image=None,
        detected_plates=[plate],
        processing_time=0.5,
    )

    assert result.success == True
    assert result.plate_count == 1


def test_detection_result_get_best_plate():
    """Test de obtención de mejor patente."""
    image = np.zeros((480, 640, 3), dtype=np.uint8)

    plate1 = PlateRegion(
        bounding_box=BoundingBox(0, 0, 100, 30), confidence=0.7, transitions_count=400
    )
    plate2 = PlateRegion(
        bounding_box=BoundingBox(200, 100, 120, 40),
        confidence=0.9,
        transitions_count=500,
    )

    result = DetectionResult(
        original_image=image,
        processed_image=None,
        detected_plates=[plate1, plate2],
    )

    best = result.get_best_plate()
    assert best == plate2  # Mayor confianza


if __name__ == "__main__":
    test_bounding_box_area()
    test_bounding_box_aspect_ratio()
    test_bounding_box_contains_point()
    test_plate_region_normalized_transitions()
    test_detection_result_success()
    test_detection_result_get_best_plate()
    print("✓ Todos los tests pasaron exitosamente!")
