"""
Ejemplo básico de detección de patentes.

Este script demuestra el uso básico del sistema de detección.
"""

import cv2
import sys
from pathlib import Path

# Agregar el directorio src al path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from plate_detector.application.plate_detection import PlateDetectionService


def main():
    """Ejemplo de detección básica."""

    # Cargar imagen de ejemplo
    image_path = Path(__file__).parent.parent / "resources" / "examples" / "img0.jpg"

    if not image_path.exists():
        print(f"Error: No se encuentra la imagen de ejemplo en {image_path}")
        print("Por favor, asegúrate de tener imágenes en resources/examples/")
        return 1

    print(f"Cargando imagen: {image_path}")
    image = cv2.imread(str(image_path))

    if image is None:
        print("Error: No se pudo cargar la imagen")
        return 1

    # Crear detector
    print("Inicializando detector de patentes...")
    detector = PlateDetectionService()

    # Detectar patentes
    print("Detectando patentes...")
    result = detector.detect(image, verbose=True)

    # Mostrar resultados
    print("\n" + "=" * 60)
    if result.success:
        print(f"✓ Detección exitosa!")
        print(f"  Patentes detectadas: {result.plate_count}")
        print(f"  Tiempo de procesamiento: {result.processing_time:.3f}s")

        for i, plate in enumerate(result.detected_plates):
            print(f"\n  Patente #{i+1}:")
            print(f"    Posición: ({plate.bounding_box.x}, {plate.bounding_box.y})")
            print(
                f"    Tamaño: {plate.bounding_box.width}x{plate.bounding_box.height}px"
            )
            print(f"    Confianza: {plate.confidence:.2%}")
            print(f"    Transiciones: {plate.transitions_count}")

        # Mostrar imagen con detecciones
        print("\nPresiona cualquier tecla para cerrar la ventana...")
        detector.display_result(result)

    else:
        print(f"✗ Error en la detección: {result.error_message}")

    print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
