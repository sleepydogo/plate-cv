"""
Filtros especializados para detección de patentes.
"""

import numpy as np
from typing import List


class TransitionFilter:
    """
    Filtro basado en transiciones de color.

    Las patentes tienen caracteres que generan transiciones blanco-negro
    características en proporciones específicas de la imagen.
    """

    def __init__(self, proportions: List[float] = None):
        """
        Inicializa el filtro de transiciones.

        Args:
            proportions: Lista de proporciones verticales donde analizar (0.0-1.0)
                        Por defecto: [0.25, 0.5, 0.75]
        """
        self.proportions = proportions or [1 / 4, 1 / 2, 3 / 4]

    def count_transitions(self, binary_image: np.ndarray) -> int:
        """
        Cuenta las transiciones de color en proporciones específicas.

        Las transiciones indican cambios de blanco a negro o viceversa,
        característicos de los caracteres de una patente.

        Args:
            binary_image: Imagen binaria a analizar

        Returns:
            Número total de transiciones detectadas
        """
        total_transitions = 0

        for proportion in self.proportions:
            # Extraer la fila en la proporción especificada
            row_index = int(binary_image.shape[0] * proportion)
            row = binary_image[row_index, :]

            # Calcular diferencias entre píxeles consecutivos
            differences = np.abs(np.diff(row))

            # Sumar transiciones (diferencias != 0)
            total_transitions += np.sum(differences)

        return total_transitions

    def get_normalized_transitions(
        self, binary_image: np.ndarray, width: int
    ) -> float:
        """
        Obtiene el valor de transiciones normalizado por el ancho.

        Args:
            binary_image: Imagen binaria a analizar
            width: Ancho de la región

        Returns:
            Valor de transiciones normalizado
        """
        total_transitions = self.count_transitions(binary_image)
        return total_transitions / (width + 1)

    def set_proportions(self, proportions: List[float]) -> None:
        """
        Actualiza las proporciones donde se analizan las transiciones.

        Args:
            proportions: Nueva lista de proporciones
        """
        if not all(0.0 <= p <= 1.0 for p in proportions):
            raise ValueError("Las proporciones deben estar entre 0.0 y 1.0")
        self.proportions = proportions


class MorphologicalFilter:
    """Filtros morfológicos para procesamiento de imágenes."""

    @staticmethod
    def erode(
        image: np.ndarray, kernel_size: int = 5, iterations: int = 1
    ) -> np.ndarray:
        """
        Aplica erosión morfológica.

        Args:
            image: Imagen a procesar
            kernel_size: Tamaño del kernel
            iterations: Número de iteraciones

        Returns:
            Imagen erosionada
        """
        import cv2

        kernel = np.ones((kernel_size, kernel_size), np.uint8)
        return cv2.erode(image, kernel, iterations=iterations)

    @staticmethod
    def dilate(
        image: np.ndarray, kernel_size: int = 5, iterations: int = 1
    ) -> np.ndarray:
        """
        Aplica dilatación morfológica.

        Args:
            image: Imagen a procesar
            kernel_size: Tamaño del kernel
            iterations: Número de iteraciones

        Returns:
            Imagen dilatada
        """
        import cv2

        kernel = np.ones((kernel_size, kernel_size), np.uint8)
        return cv2.dilate(image, kernel, iterations=iterations)

    @staticmethod
    def opening(image: np.ndarray, kernel_size: int = 5) -> np.ndarray:
        """
        Aplica apertura morfológica (erosión seguida de dilatación).

        Args:
            image: Imagen a procesar
            kernel_size: Tamaño del kernel

        Returns:
            Imagen procesada
        """
        import cv2

        kernel = np.ones((kernel_size, kernel_size), np.uint8)
        return cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)

    @staticmethod
    def closing(image: np.ndarray, kernel_size: int = 5) -> np.ndarray:
        """
        Aplica cierre morfológico (dilatación seguida de erosión).

        Args:
            image: Imagen a procesar
            kernel_size: Tamaño del kernel

        Returns:
            Imagen procesada
        """
        import cv2

        kernel = np.ones((kernel_size, kernel_size), np.uint8)
        return cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)


class EdgeDetector:
    """Detector de bordes usando diversos algoritmos."""

    @staticmethod
    def canny(
        image: np.ndarray, low_threshold: int = 50, high_threshold: int = 150
    ) -> np.ndarray:
        """
        Detecta bordes usando el algoritmo Canny.

        Args:
            image: Imagen en escala de grises
            low_threshold: Umbral inferior
            high_threshold: Umbral superior

        Returns:
            Imagen de bordes
        """
        import cv2

        return cv2.Canny(image, low_threshold, high_threshold)
