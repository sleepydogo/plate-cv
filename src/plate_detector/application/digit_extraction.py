"""
Servicio de extracción de dígitos de patentes.
"""

import cv2
import numpy as np
from typing import List, Optional

from ..domain.entities import PlateRegion, DigitRegion, BoundingBox
from ..infrastructure.image_processing.component_analysis import (
    ConnectedComponentAnalyzer,
)
from ..infrastructure.image_processing.binarization import ImageBinarizer


class DigitExtractionService:
    """
    Servicio para extraer y recortar dígitos individuales de patentes.

    Este servicio procesa una región de patente detectada para:
    1. Recortar extremos innecesarios
    2. Detectar componentes conectados (caracteres)
    3. Filtrar y extraer cada dígito/letra individual
    """

    def __init__(
        self,
        binarizer: Optional[ImageBinarizer] = None,
        component_analyzer: Optional[ConnectedComponentAnalyzer] = None,
    ):
        """
        Inicializa el servicio de extracción de dígitos.

        Args:
            binarizer: Binarizador de imágenes
            component_analyzer: Analizador de componentes conectados
        """
        self.binarizer = binarizer or ImageBinarizer(threshold=140)
        self.component_analyzer = component_analyzer or ConnectedComponentAnalyzer()

    def extract_digits(
        self, plate_region: PlateRegion, verbose: bool = False
    ) -> List[DigitRegion]:
        """
        Extrae los dígitos individuales de una región de patente.

        Args:
            plate_region: Región de patente detectada
            verbose: Si True, muestra información de depuración

        Returns:
            Lista de regiones de dígitos detectados
        """
        if plate_region.image_data is None:
            raise ValueError("La región de patente no contiene datos de imagen")

        # 1. Binarizar si es necesario
        if len(plate_region.image_data.shape) == 3:
            gray = cv2.cvtColor(plate_region.image_data, cv2.COLOR_BGR2GRAY)
        else:
            gray = plate_region.image_data

        binary_plate = self.binarizer.binarize(gray)

        # 2. Recortar extremos de la patente
        cropped_plate = self._crop_plate_margins(binary_plate)

        # 3. Detectar componentes (dígitos/letras)
        digit_regions = self._detect_digits(cropped_plate, verbose)

        if verbose:
            print(f"Dígitos detectados: {len(digit_regions)}")

        return digit_regions

    def _crop_plate_margins(
        self, binary_plate: np.ndarray, intensity_threshold: int = 100
    ) -> np.ndarray:
        """
        Recorta los márgenes superior e inferior de la patente.

        Elimina filas que tienen baja densidad de píxeles blancos,
        lo que indica que son márgenes sin contenido útil.

        Args:
            binary_plate: Imagen binaria de la patente
            intensity_threshold: Umbral de intensidad promedio por fila

        Returns:
            Imagen recortada
        """
        height, width = binary_plate.shape[:2]
        rows_to_remove = []

        # Analizar cada fila
        for i in range(height):
            row_sum = np.sum(binary_plate[i, :])
            row_average = row_sum / width

            # Si el promedio es menor al umbral, marcar para eliminar
            if row_average < intensity_threshold:
                rows_to_remove.append(i)

        # Eliminar las últimas 15 filas (margen inferior)
        rows_to_remove.extend(range(height - 15, height))

        # Eliminar filas marcadas
        cropped = np.delete(binary_plate, rows_to_remove, axis=0)

        return cropped

    def _detect_digits(
        self, cropped_plate: np.ndarray, verbose: bool
    ) -> List[DigitRegion]:
        """
        Detecta componentes conectados que corresponden a dígitos.

        Args:
            cropped_plate: Imagen de patente recortada
            verbose: Modo verbose

        Returns:
            Lista de regiones de dígitos
        """
        height, width = cropped_plate.shape[:2]

        # Invertir la imagen para que los caracteres sean blancos
        inverted = cv2.bitwise_not(cropped_plate)

        # Detectar componentes conectados
        _, stats, bounding_boxes = self.component_analyzer.find_components(inverted)

        # Calcular límites de área
        total_area = width * height
        max_area = total_area / 6
        min_area = total_area / 62

        digit_regions = []

        for bb in bounding_boxes:
            # Filtrar por área
            if min_area <= bb.area <= max_area:
                # Extraer ROI del dígito
                digit_roi = self.component_analyzer.extract_roi(cropped_plate, bb)

                digit_region = DigitRegion(
                    bounding_box=bb,
                    image_data=digit_roi,
                    confidence=1.0,  # Podría mejorarse con análisis adicional
                )

                digit_regions.append(digit_region)

                if verbose:
                    print(
                        f"Dígito detectado: área={bb.area}, "
                        f"tamaño={bb.width}x{bb.height}"
                    )

        # Ordenar de izquierda a derecha (orden de lectura)
        digit_regions.sort(key=lambda d: d.bounding_box.x)

        return digit_regions

    def save_digit_images(
        self, digit_regions: List[DigitRegion], output_dir: str, prefix: str = "digit"
    ) -> List[str]:
        """
        Guarda las imágenes de los dígitos en archivos.

        Args:
            digit_regions: Lista de regiones de dígitos
            output_dir: Directorio de salida
            prefix: Prefijo para los nombres de archivo

        Returns:
            Lista de rutas de archivos guardados
        """
        import os

        os.makedirs(output_dir, exist_ok=True)
        saved_paths = []

        for i, digit in enumerate(digit_regions):
            if digit.image_data is not None:
                filename = f"{prefix}_{i:03d}.jpg"
                filepath = os.path.join(output_dir, filename)
                cv2.imwrite(filepath, digit.image_data)
                saved_paths.append(filepath)

        return saved_paths

    def visualize_digits(self, digit_regions: List[DigitRegion]) -> None:
        """
        Visualiza los dígitos detectados en ventanas separadas.

        Args:
            digit_regions: Lista de regiones de dígitos
        """
        for i, digit in enumerate(digit_regions):
            if digit.image_data is not None:
                cv2.imshow(f"Dígito {i}", digit.image_data)

        cv2.waitKey(0)
        cv2.destroyAllWindows()
