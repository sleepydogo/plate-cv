"""
Generador de templates a partir de dígitos recortados.
"""

import os
import cv2
import numpy as np
from typing import List, Optional


class TemplateGenerator:
    """
    Genera templates de dígitos para reconocimiento posterior.

    Este módulo permite procesar un conjunto de imágenes de patentes,
    extraer los dígitos individuales y guardarlos como templates.
    """

    def __init__(self, output_dir: str = "resources/templates"):
        """
        Inicializa el generador de templates.

        Args:
            output_dir: Directorio donde guardar los templates generados
        """
        self.output_dir = output_dir
        self.counter = 0

    def save_template(
        self, digit_image: np.ndarray, label: Optional[str] = None
    ) -> str:
        """
        Guarda un template de dígito.

        Args:
            digit_image: Imagen del dígito
            label: Etiqueta del dígito (opcional)

        Returns:
            Ruta del archivo guardado
        """
        os.makedirs(self.output_dir, exist_ok=True)

        if label:
            filename = f"template_{label}_{self.counter:04d}.jpg"
        else:
            filename = f"template_{self.counter:04d}.jpg"

        filepath = os.path.join(self.output_dir, filename)
        cv2.imwrite(filepath, digit_image)

        self.counter += 1
        print(f"Template guardado: {filepath}")

        return filepath

    def generate_from_images(
        self, image_paths: List[str], process_callback=None
    ) -> int:
        """
        Genera templates desde una lista de imágenes de patentes.

        Args:
            image_paths: Lista de rutas de imágenes
            process_callback: Función callback para procesar cada imagen

        Returns:
            Número de templates generados
        """
        initial_count = self.counter

        for image_path in image_paths:
            if not os.path.exists(image_path):
                print(f"Archivo no encontrado: {image_path}")
                continue

            if process_callback:
                templates = process_callback(image_path)
                for template in templates:
                    self.save_template(template)

        return self.counter - initial_count

    def reset_counter(self) -> None:
        """Reinicia el contador de templates."""
        self.counter = 0

    def organize_templates_by_label(self, source_dir: str, target_dir: str) -> None:
        """
        Organiza templates en subdirectorios según su etiqueta.

        Args:
            source_dir: Directorio fuente con templates
            target_dir: Directorio destino organizado
        """
        os.makedirs(target_dir, exist_ok=True)

        for filename in os.listdir(source_dir):
            if not filename.endswith((".jpg", ".png")):
                continue

            # Intentar extraer etiqueta del nombre
            # Formato esperado: template_LABEL_0001.jpg
            parts = filename.split("_")
            if len(parts) >= 3:
                label = parts[1]
                label_dir = os.path.join(target_dir, label)
                os.makedirs(label_dir, exist_ok=True)

                source_path = os.path.join(source_dir, filename)
                target_path = os.path.join(label_dir, filename)

                # Mover o copiar archivo
                import shutil

                shutil.copy2(source_path, target_path)
