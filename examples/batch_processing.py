"""
Ejemplo de procesamiento por lotes.

Procesa múltiples imágenes y genera un reporte.
"""

import cv2
import sys
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from plate_detector.application.plate_detection import PlateDetectionService


def process_batch(image_dir: Path, output_dir: Path):
    """Procesa un lote de imágenes."""

    # Crear detector
    detector = PlateDetectionService()

    # Buscar imágenes
    image_extensions = [".jpg", ".jpeg", ".png"]
    images = []
    for ext in image_extensions:
        images.extend(image_dir.glob(f"*{ext}"))

    if not images:
        print(f"No se encontraron imágenes en {image_dir}")
        return

    print(f"Encontradas {len(images)} imágenes")
    print("=" * 60)

    results_data = []

    # Procesar cada imagen
    for i, image_path in enumerate(images, 1):
        print(f"\n[{i}/{len(images)}] Procesando: {image_path.name}")

        image = cv2.imread(str(image_path))
        if image is None:
            print(f"  ✗ Error al cargar imagen")
            continue

        # Detectar
        result = detector.detect(image, verbose=False)

        if result.success:
            print(f"  ✓ Detectadas {result.plate_count} patentes")

            # Guardar imagen con detecciones
            if result.processed_image is not None:
                output_path = output_dir / f"result_{image_path.name}"
                cv2.imwrite(str(output_path), result.processed_image)
                print(f"  → Guardado en: {output_path}")

            # Agregar a reporte
            results_data.append(
                {
                    "filename": image_path.name,
                    "success": True,
                    "plate_count": result.plate_count,
                    "processing_time": result.processing_time,
                    "plates": [
                        {
                            "confidence": p.confidence,
                            "position": {
                                "x": p.bounding_box.x,
                                "y": p.bounding_box.y,
                                "width": p.bounding_box.width,
                                "height": p.bounding_box.height,
                            },
                        }
                        for p in result.detected_plates
                    ],
                }
            )
        else:
            print(f"  ✗ Error: {result.error_message}")
            results_data.append(
                {
                    "filename": image_path.name,
                    "success": False,
                    "error": result.error_message,
                }
            )

    # Generar reporte
    report = {
        "timestamp": datetime.now().isoformat(),
        "total_images": len(images),
        "successful": sum(1 for r in results_data if r.get("success", False)),
        "results": results_data,
    }

    report_path = output_dir / "batch_report.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    print("\n" + "=" * 60)
    print("RESUMEN:")
    print(f"  Total de imágenes: {report['total_images']}")
    print(f"  Exitosas: {report['successful']}")
    print(
        f"  Tasa de éxito: {report['successful']/report['total_images']*100:.1f}%"
    )
    print(f"\nReporte guardado en: {report_path}")
    print("=" * 60)


def main():
    """Punto de entrada principal."""

    # Directorios
    base_dir = Path(__file__).parent.parent
    image_dir = base_dir / "resources" / "examples"
    output_dir = base_dir / "output" / "batch_results"

    # Crear directorio de salida
    output_dir.mkdir(parents=True, exist_ok=True)

    # Procesar lote
    process_batch(image_dir, output_dir)

    return 0


if __name__ == "__main__":
    sys.exit(main())
