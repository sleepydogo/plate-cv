"""
Módulo de binarización de imágenes.
"""

import cv2
import numpy as np
from typing import Tuple


class ImageBinarizer:
    """Realiza binarización de imágenes en escala de grises."""

    def __init__(self, threshold: int = 150):
        """
        Inicializa el binarizador.

        Args:
            threshold: Umbral global para binarización (0-255)
        """
        self.threshold = threshold

    def binarize(self, image: np.ndarray) -> np.ndarray:
        """
        Binariza una imagen en escala de grises.

        Args:
            image: Imagen en escala de grises

        Returns:
            Imagen binarizada (valores 0 o 255)
        """
        if len(image.shape) != 2:
            raise ValueError("La imagen debe estar en escala de grises")

        _, binary_image = cv2.threshold(
            image, self.threshold, 255, cv2.THRESH_BINARY
        )
        return binary_image

    def adaptive_binarize(
        self, image: np.ndarray, block_size: int = 11, c: int = 2
    ) -> np.ndarray:
        """
        Binarización adaptativa usando umbral local.

        Args:
            image: Imagen en escala de grises
            block_size: Tamaño del bloque para calcular umbral local (debe ser impar)
            c: Constante que se resta del promedio

        Returns:
            Imagen binarizada adaptivamente
        """
        if block_size % 2 == 0:
            block_size += 1

        return cv2.adaptiveThreshold(
            image,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            block_size,
            c,
        )

    def binarize_with_otsu(self, image: np.ndarray) -> Tuple[np.ndarray, int]:
        """
        Binariza usando el método de Otsu (umbral automático).

        Args:
            image: Imagen en escala de grises

        Returns:
            Tupla (imagen_binarizada, umbral_calculado)
        """
        threshold_value, binary_image = cv2.threshold(
            image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )
        return binary_image, int(threshold_value)

    def set_threshold(self, threshold: int) -> None:
        """
        Actualiza el umbral de binarización.

        Args:
            threshold: Nuevo valor de umbral (0-255)
        """
        if not 0 <= threshold <= 255:
            raise ValueError("El umbral debe estar entre 0 y 255")
        self.threshold = threshold
