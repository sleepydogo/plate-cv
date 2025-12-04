# Guía del Usuario - Plate Detector

## Introducción

Plate Detector es un sistema de detección de patentes argentinas diseñado para funcionar con recursos mínimos, ideal para Raspberry Pi y microcontroladores.

## Instalación

### Requisitos del Sistema

- Python 3.8 o superior
- 2 GB RAM mínimo (recomendado: 4 GB)
- OpenCV compatible con su sistema

### Instalación Paso a Paso

1. **Clonar el repositorio**:
```bash
git clone https://github.com/sleepydogo/plate-cv.git
cd plate-cv
```

2. **Crear entorno virtual** (recomendado):
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. **Instalar dependencias**:
```bash
pip install -r requirements.txt
```

4. **Verificar instalación**:
```bash
python -m plate_detector.interfaces.cli --help
```

## Uso Básico

### 1. Detectar Patentes

#### Detección Simple

```bash
python -m plate_detector.interfaces.cli detect imagen.jpg --show
```

Este comando:
- Carga `imagen.jpg`
- Detecta patentes
- Muestra resultado en pantalla

#### Guardar Resultado

```bash
python -m plate_detector.interfaces.cli detect imagen.jpg --output resultado.jpg
```

La imagen `resultado.jpg` contendrá las patentes detectadas marcadas con rectángulos verdes.

#### Modo Verbose (Depuración)

```bash
python -m plate_detector.interfaces.cli detect imagen.jpg --verbose
```

Muestra información detallada:
- Componentes detectados en cada etapa
- Valores de transiciones
- Criterios de filtrado
- Tiempo de procesamiento

### 2. Extraer Dígitos

Una vez detectada una patente, puedes extraer sus dígitos individuales:

```bash
python -m plate_detector.interfaces.cli extract imagen.jpg --output ./digits/ --show
```

Esto:
1. Detecta la patente en la imagen
2. Extrae cada dígito/letra individual
3. Guarda cada dígito en `./digits/`
4. Muestra los dígitos en pantalla

## Configuraciones Avanzadas

### Perfiles de Configuración

#### Default (Balanceado)

```bash
python -m plate_detector.interfaces.cli detect imagen.jpg --config default
```

Configuración estándar, funciona bien en la mayoría de casos.

#### High Sensitivity (Alta Sensibilidad)

```bash
python -m plate_detector.interfaces.cli detect imagen.jpg --config high_sensitivity
```

Usa cuando:
- Las condiciones de iluminación son malas
- La patente está parcialmente oculta
- Prefieres más candidatos (aunque algunos sean falsos positivos)

**Parámetros ajustados**:
- Rango de área más amplio (hasta 400)
- Transiciones más permisivas (25-100)

#### High Precision (Alta Precisión)

```bash
python -m plate_detector.interfaces.cli detect imagen.jpg --config high_precision
```

Usa cuando:
- Necesitas máxima certeza
- Prefieres perder algunas detecciones antes que tener falsos positivos
- La imagen tiene buena calidad

**Parámetros ajustados**:
- Relación de aspecto más estricta (3.0-4.5)
- Transiciones más restrictivas (40-80)

## Uso Programático

### Ejemplo Básico

```python
import cv2
from plate_detector.application.plate_detection import PlateDetectionService

# Cargar imagen
image = cv2.imread("mi_imagen.jpg")

# Crear detector
detector = PlateDetectionService()

# Detectar
result = detector.detect(image)

# Verificar resultado
if result.success:
    print(f"Detectadas {result.plate_count} patentes")
    for i, plate in enumerate(result.detected_plates):
        print(f"Patente {i+1}: confianza {plate.confidence:.2%}")
else:
    print(f"Error: {result.error_message}")
```

### Ejemplo con Configuración Personalizada

```python
from plate_detector.application.plate_detection import PlateDetectionService
from plate_detector.infrastructure.image_processing import (
    ImageBinarizer,
    ConnectedComponentAnalyzer,
    TransitionFilter
)
from plate_detector.domain.validators import PlateValidator

# Configurar componentes personalizados
binarizer = ImageBinarizer(threshold=160)  # Umbral personalizado
transition_filter = TransitionFilter(proportions=[0.2, 0.5, 0.8])

# Crear servicio con configuración personalizada
detector = PlateDetectionService(
    binarizer=binarizer,
    transition_filter=transition_filter,
)

# Usar normalmente
result = detector.detect(image, verbose=True)
```

### Extraer Dígitos Programáticamente

```python
from plate_detector.application.digit_extraction import DigitExtractionService

# Primero detectar patente
detector = PlateDetectionService()
result = detector.detect(image)

if result.success:
    # Obtener mejor patente
    best_plate = result.get_best_plate()

    # Extraer dígitos
    extractor = DigitExtractionService()
    digits = extractor.extract_digits(best_plate, verbose=True)

    # Guardar dígitos
    extractor.save_digit_images(digits, output_dir="./output/")
```

## Casos de Uso Comunes

### 1. Procesar múltiples imágenes

```python
import os
import cv2
from plate_detector import PlateDetectionService

detector = PlateDetectionService()
image_dir = "resources/examples/"

for filename in os.listdir(image_dir):
    if filename.endswith(('.jpg', '.png')):
        image_path = os.path.join(image_dir, filename)
        image = cv2.imread(image_path)

        result = detector.detect(image)
        print(f"{filename}: {result.plate_count} patentes")
```

### 2. Detección en tiempo real (video/webcam)

```python
import cv2
from plate_detector import PlateDetectionService

detector = PlateDetectionService()
cap = cv2.VideoCapture(0)  # 0 = webcam

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Detectar cada N frames para mejor performance
    result = detector.detect(frame)

    # Dibujar resultados
    if result.success:
        for plate in result.detected_plates:
            bb = plate.bounding_box
            cv2.rectangle(frame,
                         (bb.x, bb.y),
                         (bb.x + bb.width, bb.y + bb.height),
                         (0, 255, 0), 2)

    cv2.imshow('Detección en Tiempo Real', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
```

### 3. Guardar estadísticas

```python
import json
from plate_detector import PlateDetectionService

detector = PlateDetectionService()
image = cv2.imread("imagen.jpg")
result = detector.detect(image)

# Crear reporte
report = {
    "success": result.success,
    "plate_count": result.plate_count,
    "processing_time": result.processing_time,
    "plates": [
        {
            "position": (p.bounding_box.x, p.bounding_box.y),
            "size": (p.bounding_box.width, p.bounding_box.height),
            "confidence": p.confidence,
            "transitions": p.transitions_count
        }
        for p in result.detected_plates
    ]
}

# Guardar en JSON
with open("resultado.json", "w") as f:
    json.dump(report, f, indent=2)
```

## Optimización de Rendimiento

### Para Raspberry Pi

```python
from plate_detector.config import PlateDetectorConfig

# Configuración optimizada para bajo consumo
config = PlateDetectorConfig()
config.binarization.threshold = 150  # Umbral fijo (más rápido)
config.verbose = False  # Desactivar logs

# Usar imágenes de menor resolución
image = cv2.imread("imagen.jpg")
small_image = cv2.resize(image, (640, 480))  # Reducir tamaño

result = detector.detect(small_image)
```

### Procesamiento por lotes

```python
import cv2
from pathlib import Path

detector = PlateDetectionService()
images_path = Path("resources/examples/")

# Procesar en lote
results = []
for img_path in images_path.glob("*.jpg"):
    image = cv2.imread(str(img_path))
    result = detector.detect(image)
    results.append((img_path.name, result))

# Análisis
total = len(results)
successful = sum(1 for _, r in results if r.success)
print(f"Éxito: {successful}/{total} ({successful/total*100:.1f}%)")
```

## Solución de Problemas

### No se detectan patentes

**Síntomas**: `result.plate_count == 0`

**Soluciones**:
1. Usar configuración `high_sensitivity`
2. Ajustar umbral de binarización:
   ```python
   detector.binarizer.set_threshold(120)  # Probar valores 100-180
   ```
3. Verificar calidad de imagen (resolución, iluminación)
4. Activar modo `verbose` para ver dónde falla el pipeline

### Demasiados falsos positivos

**Síntomas**: Detecta regiones que no son patentes

**Soluciones**:
1. Usar configuración `high_precision`
2. Ajustar validadores:
   ```python
   from plate_detector.domain.validators import PlateValidator
   validator = PlateValidator()
   validator.transition_validator.min_transitions = 45  # Más estricto
   ```

### Errores de memoria en Raspberry Pi

**Soluciones**:
1. Reducir resolución de imágenes
2. Procesar una imagen a la vez
3. Liberar memoria explícitamente:
   ```python
   import gc
   result = detector.detect(image)
   # Procesar resultado
   del result
   gc.collect()
   ```

## Recursos Adicionales

- [Documentación de Arquitectura](architecture.md)
- [Referencia de API](api_reference.md)
- [Notebook de Desarrollo](../notebooks/development_process.ipynb)

## Soporte

Para reportar bugs o solicitar features:
- GitHub Issues: [https://github.com/sleepydogo/plate-cv/issues](https://github.com/sleepydogo/plate-cv/issues)
