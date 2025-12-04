"""
Análisis de componentes conectados para detección de regiones.
"""

import cv2
import numpy as np
from typing import List, Tuple
from ...domain.entities import BoundingBox


class ConnectedComponentAnalyzer:
    """Analiza componentes conectados en imágenes binarias."""

    def __init__(self):
        """Inicializa el analizador de componentes conectados."""
        pass

    def find_components(
        self, binary_image: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray, List[BoundingBox]]:
        """
        Encuentra componentes conectados en una imagen binaria.

        Args:
            binary_image: Imagen binarizada

        Returns:
            Tupla (labels, stats, bounding_boxes):
                - labels: Matriz de etiquetas de componentes
                - stats: Estadísticas de componentes
                - bounding_boxes: Lista de BoundingBox para cada componente
        """
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(
            binary_image
        )

        # Convertir stats a BoundingBox (saltando el fondo en índice 0)
        bounding_boxes = []
        for i in range(1, len(stats)):
            x, y, w, h, area = stats[i]
            bounding_boxes.append(BoundingBox(x=x, y=y, width=w, height=h))

        return labels, stats, bounding_boxes

    def extract_roi(
        self, image: np.ndarray, bounding_box: BoundingBox
    ) -> np.ndarray:
        """
        Extrae una región de interés de la imagen.

        Args:
            image: Imagen fuente
            bounding_box: Cuadro delimitador de la región

        Returns:
            Región extraída
        """
        return image[
            bounding_box.y : bounding_box.y + bounding_box.height,
            bounding_box.x : bounding_box.x + bounding_box.width,
        ].copy()

    def filter_by_area(
        self, bounding_boxes: List[BoundingBox], min_area: int, max_area: int
    ) -> List[BoundingBox]:
        """
        Filtra componentes por área.

        Args:
            bounding_boxes: Lista de bounding boxes
            min_area: Área mínima
            max_area: Área máxima

        Returns:
            Lista filtrada de bounding boxes
        """
        return [
            bb for bb in bounding_boxes if min_area <= bb.area <= max_area
        ]

    def filter_by_aspect_ratio(
        self,
        bounding_boxes: List[BoundingBox],
        min_ratio: float,
        max_ratio: float,
    ) -> List[BoundingBox]:
        """
        Filtra componentes por relación de aspecto.

        Args:
            bounding_boxes: Lista de bounding boxes
            min_ratio: Relación de aspecto mínima
            max_ratio: Relación de aspecto máxima

        Returns:
            Lista filtrada de bounding boxes
        """
        return [
            bb
            for bb in bounding_boxes
            if min_ratio <= bb.aspect_ratio <= max_ratio
        ]

    def remove_component(
        self, labels: np.ndarray, label_to_remove: int
    ) -> np.ndarray:
        """
        Elimina un componente específico de la matriz de etiquetas.

        Args:
            labels: Matriz de etiquetas
            label_to_remove: Etiqueta del componente a eliminar

        Returns:
            Matriz de etiquetas actualizada
        """
        labels[labels == label_to_remove] = 0
        return labels

    def draw_bounding_boxes(
        self,
        image: np.ndarray,
        bounding_boxes: List[BoundingBox],
        color: Tuple[int, int, int] = (0, 255, 0),
        thickness: int = 2,
    ) -> np.ndarray:
        """
        Dibuja bounding boxes en una imagen.

        Args:
            image: Imagen donde dibujar
            bounding_boxes: Lista de bounding boxes a dibujar
            color: Color BGR del rectángulo
            thickness: Grosor de las líneas

        Returns:
            Imagen con bounding boxes dibujados
        """
        result = image.copy()
        for bb in bounding_boxes:
            cv2.rectangle(
                result,
                (bb.x, bb.y),
                (bb.x + bb.width, bb.y + bb.height),
                color,
                thickness,
            )
        return result
