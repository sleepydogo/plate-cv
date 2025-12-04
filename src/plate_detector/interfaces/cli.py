"""
Interfaz de línea de comandos (CLI) para el detector de patentes.
"""

import argparse
import sys
import cv2
from pathlib import Path
from typing import Optional

from ..application.plate_detection import PlateDetectionService
from ..application.digit_extraction import DigitExtractionService
from ..config import PlateDetectorConfig


def detect_command(args):
    """
    Comando para detectar patentes en una imagen.

    Args:
        args: Argumentos de línea de comandos
    """
    # Cargar imagen
    image_path = Path(args.image)
    if not image_path.exists():
        print(f"Error: No se encuentra la imagen '{image_path}'")
        return 1

    image = cv2.imread(str(image_path))
    if image is None:
        print(f"Error: No se pudo cargar la imagen '{image_path}'")
        return 1

    # Configurar detector
    if args.config == "default":
        config = PlateDetectorConfig.default()
    elif args.config == "high_sensitivity":
        config = PlateDetectorConfig.high_sensitivity()
    elif args.config == "high_precision":
        config = PlateDetectorConfig.high_precision()
    else:
        config = PlateDetectorConfig.default()

    config.verbose = args.verbose

    # Crear servicio de detección
    detector = PlateDetectionService()

    # Detectar patentes
    print(f"Procesando imagen: {image_path}")
    result = detector.detect(image, verbose=args.verbose)

    # Mostrar resultados
    if result.success:
        print(f"\n{'='*60}")
        print(f"Patentes detectadas: {result.plate_count}")
        print(f"Tiempo de procesamiento: {result.processing_time:.3f}s")
        print(f"{'='*60}\n")

        for i, plate in enumerate(result.detected_plates):
            print(f"Patente #{i+1}:")
            print(f"  Posición: ({plate.bounding_box.x}, {plate.bounding_box.y})")
            print(f"  Tamaño: {plate.bounding_box.width}x{plate.bounding_box.height}")
            print(f"  Confianza: {plate.confidence:.2%}")
            print(f"  Transiciones: {plate.transitions_count}")
            print()

        # Guardar resultado si se especifica
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            output_image = detector._draw_results(image.copy(), result.detected_plates)
            cv2.imwrite(str(output_path), output_image)
            print(f"Resultado guardado en: {output_path}")

        # Mostrar si se solicita
        if args.show and result.processed_image is not None:
            detector.display_result(result)

    else:
        print(f"Error en la detección: {result.error_message}")
        return 1

    return 0


def extract_digits_command(args):
    """
    Comando para extraer dígitos de una imagen de patente.

    Args:
        args: Argumentos de línea de comandos
    """
    # Cargar imagen
    image_path = Path(args.image)
    if not image_path.exists():
        print(f"Error: No se encuentra la imagen '{image_path}'")
        return 1

    image = cv2.imread(str(image_path))
    if image is None:
        print(f"Error: No se pudo cargar la imagen '{image_path}'")
        return 1

    # Primero detectar la patente
    detector = PlateDetectionService()
    result = detector.detect(image, verbose=args.verbose)

    if not result.success or result.plate_count == 0:
        print("No se detectaron patentes en la imagen")
        return 1

    # Usar la patente con mayor confianza
    plate = result.get_best_plate()
    print(f"Extrayendo dígitos de patente con confianza: {plate.confidence:.2%}")

    # Extraer dígitos
    extractor = DigitExtractionService()
    digits = extractor.extract_digits(plate, verbose=args.verbose)

    print(f"\nDígitos detectados: {len(digits)}")

    # Guardar dígitos si se especifica directorio de salida
    if args.output:
        output_dir = Path(args.output)
        saved_paths = extractor.save_digit_images(
            digits, str(output_dir), prefix=args.prefix
        )
        print(f"\n{len(saved_paths)} dígitos guardados en: {output_dir}")

    # Mostrar dígitos si se solicita
    if args.show:
        extractor.visualize_digits(digits)

    return 0


def main():
    """Punto de entrada principal del CLI."""
    parser = argparse.ArgumentParser(
        description="Detector de Patentes Argentinas usando Procesamiento Clásico de Imágenes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:

  # Detectar patentes en una imagen
  python -m plate_detector.interfaces.cli detect imagen.jpg --show

  # Detectar con alta sensibilidad y guardar resultado
  python -m plate_detector.interfaces.cli detect imagen.jpg --config high_sensitivity --output resultado.jpg

  # Extraer dígitos de una patente
  python -m plate_detector.interfaces.cli extract imagen.jpg --output ./digits/ --show

  # Modo verbose para debugging
  python -m plate_detector.interfaces.cli detect imagen.jpg --verbose
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Comandos disponibles")

    # Comando: detect
    detect_parser = subparsers.add_parser(
        "detect", help="Detectar patentes en una imagen"
    )
    detect_parser.add_argument("image", help="Ruta de la imagen a procesar")
    detect_parser.add_argument(
        "--config",
        choices=["default", "high_sensitivity", "high_precision"],
        default="default",
        help="Configuración del detector",
    )
    detect_parser.add_argument(
        "--output", "-o", help="Ruta para guardar la imagen con detecciones"
    )
    detect_parser.add_argument(
        "--show", "-s", action="store_true", help="Mostrar resultado en pantalla"
    )
    detect_parser.add_argument(
        "--verbose", "-v", action="store_true", help="Modo verbose (debug)"
    )

    # Comando: extract
    extract_parser = subparsers.add_parser(
        "extract", help="Extraer dígitos de una patente"
    )
    extract_parser.add_argument("image", help="Ruta de la imagen con patente")
    extract_parser.add_argument(
        "--output", "-o", help="Directorio para guardar los dígitos extraídos"
    )
    extract_parser.add_argument(
        "--prefix", default="digit", help="Prefijo para nombres de archivos"
    )
    extract_parser.add_argument(
        "--show", "-s", action="store_true", help="Mostrar dígitos en pantalla"
    )
    extract_parser.add_argument(
        "--verbose", "-v", action="store_true", help="Modo verbose (debug)"
    )

    # Parsear argumentos
    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return 0

    # Ejecutar comando
    if args.command == "detect":
        return detect_command(args)
    elif args.command == "extract":
        return extract_digits_command(args)

    return 0


if __name__ == "__main__":
    sys.exit(main())
