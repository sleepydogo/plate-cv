"""
Servicio principal de detección de patentes.
"""

import cv2
import numpy as np
import time
from typing import List, Optional

from ..domain.entities import PlateRegion, DetectionResult, BoundingBox
from ..domain.validators import PlateValidator
from ..infrastructure.image_processing.binarization import ImageBinarizer
from ..infrastructure.image_processing.component_analysis import (
    ConnectedComponentAnalyzer,
)
from ..infrastructure.image_processing.filters import TransitionFilter


class PlateDetectionService:
    """
    Servicio de detección de patentes usando procesamiento clásico de imágenes.

    Este servicio implementa el pipeline completo:
    1. Binarización de imagen
    2. Análisis de componentes conectados
    3. Filtrado por criterios geométricos
    4. Filtrado por transiciones de color
    """

    def __init__(
        self,
        binarizer: Optional[ImageBinarizer] = None,
        component_analyzer: Optional[ConnectedComponentAnalyzer] = None,
        transition_filter: Optional[TransitionFilter] = None,
        validator: Optional[PlateValidator] = None,
    ):
        """
        Inicializa el servicio de detección.

        Args:
            binarizer: Binarizador de imágenes
            component_analyzer: Analizador de componentes conectados
            transition_filter: Filtro de transiciones
            validator: Validador de regiones de patentes
        """
        self.binarizer = binarizer or ImageBinarizer(threshold=150)
        self.component_analyzer = component_analyzer or ConnectedComponentAnalyzer()
        self.transition_filter = transition_filter or TransitionFilter()
        self.validator = validator or PlateValidator()

    def detect(
        self, image: np.ndarray, verbose: bool = False
    ) -> DetectionResult:
        """
        Detecta patentes en una imagen.

        Args:
            image: Imagen a procesar (RGB o escala de grises)
            verbose: Si True, muestra información de depuración

        Returns:
            DetectionResult con las patentes detectadas
        """
        start_time = time.time()

        try:
            # Convertir a escala de grises si es necesario
            if len(image.shape) == 3:
                gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray_image = image

            # 1. Binarización
            binary_image = self.binarizer.binarize(gray_image)

            # 2. Análisis de componentes conectados
            labels, stats, bounding_boxes = self.component_analyzer.find_components(
                binary_image
            )

            # 3. Filtrado inicial por criterios geométricos
            total_area = binary_image.size
            filtered_boxes = self._filter_by_geometry(
                bounding_boxes, total_area, verbose
            )

            # 4. Filtrado por transiciones de color
            candidate_plates = self._filter_by_transitions(
                filtered_boxes, binary_image, verbose
            )

            # 5. Validación final
            valid_plates = self._validate_candidates(
                candidate_plates, total_area, verbose
            )

            processing_time = time.time() - start_time

            # Dibujar resultados si verbose
            result_image = None
            if verbose and len(valid_plates) > 0:
                result_image = self._draw_results(image.copy(), valid_plates)

            return DetectionResult(
                original_image=image,
                processed_image=result_image,
                detected_plates=valid_plates,
                processing_time=processing_time,
                success=True,
            )

        except Exception as e:
            processing_time = time.time() - start_time
            return DetectionResult(
                original_image=image,
                processed_image=None,
                detected_plates=[],
                processing_time=processing_time,
                success=False,
                error_message=str(e),
            )

    def _filter_by_geometry(
        self, bounding_boxes: List[BoundingBox], total_area: int, verbose: bool
    ) -> List[BoundingBox]:
        """Filtra componentes por criterios geométricos."""
        filtered = []

        for bb in bounding_boxes:
            # Filtro por relación de aspecto (ancho/alto entre 2.8 y 5)
            if not (2.8 <= bb.aspect_ratio <= 5.0):
                continue

            # Filtro por relación de área
            area_ratio = total_area / bb.area if bb.area > 0 else 0
            if not (23 <= area_ratio <= 300):
                continue

            filtered.append(bb)

        if verbose:
            print(f"Componentes después de filtro geométrico: {len(filtered)}")

        return filtered

    def _filter_by_transitions(
        self,
        bounding_boxes: List[BoundingBox],
        binary_image: np.ndarray,
        verbose: bool,
    ) -> List[PlateRegion]:
        """Filtra componentes por transiciones de color."""
        candidate_plates = []

        for bb in bounding_boxes:
            # Extraer ROI
            roi = self.component_analyzer.extract_roi(binary_image, bb)

            # Contar transiciones
            total_transitions = self.transition_filter.count_transitions(roi)
            normalized_value = total_transitions / (bb.width + 1)

            if verbose:
                print(
                    f"Transiciones: {total_transitions}, "
                    f"Normalizado: {normalized_value:.2f}"
                )

            # Verificar rango de transiciones normalizadas (30-90)
            if 30 <= normalized_value <= 90:
                # Calcular confianza basada en qué tan cerca está del rango ideal
                confidence = self._calculate_confidence(normalized_value)

                plate_region = PlateRegion(
                    bounding_box=bb,
                    confidence=confidence,
                    transitions_count=total_transitions,
                    image_data=roi,
                )
                candidate_plates.append(plate_region)

        if verbose:
            print(f"Candidatos después de filtro de transiciones: {len(candidate_plates)}")

        return candidate_plates

    def _validate_candidates(
        self,
        candidates: List[PlateRegion],
        total_area: int,
        verbose: bool,
    ) -> List[PlateRegion]:
        """Valida los candidatos finales."""
        valid_plates = []

        for plate in candidates:
            is_valid, message = self.validator.validate_plate_region(
                plate, total_area
            )

            if is_valid:
                valid_plates.append(plate)
            elif verbose:
                print(f"Candidato rechazado: {message}")

        if verbose:
            print(f"Patentes válidas detectadas: {len(valid_plates)}")

        return valid_plates

    def _calculate_confidence(self, normalized_transitions: float) -> float:
        """
        Calcula la confianza basada en el valor de transiciones.

        El valor ideal está alrededor de 60 (centro del rango 30-90).
        """
        ideal_value = 60.0
        max_deviation = 30.0

        deviation = abs(normalized_transitions - ideal_value)
        confidence = max(0.0, 1.0 - (deviation / max_deviation))

        return confidence

    def _draw_results(
        self, image: np.ndarray, plates: List[PlateRegion]
    ) -> np.ndarray:
        """Dibuja los resultados de detección en la imagen."""
        bounding_boxes = [plate.bounding_box for plate in plates]
        return self.component_analyzer.draw_bounding_boxes(
            image, bounding_boxes, color=(0, 255, 0), thickness=2
        )

    def display_result(self, result: DetectionResult, window_size: tuple = (700, 700)):
        """
        Muestra el resultado de la detección en una ventana.

        Args:
            result: Resultado de la detección
            window_size: Tamaño de la ventana (ancho, alto)
        """
        if result.processed_image is not None:
            resized = cv2.resize(
                result.processed_image, window_size, interpolation=cv2.INTER_AREA
            )
            cv2.imshow("Detección de Patentes", resized)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        else:
            print("No hay imagen procesada para mostrar")
