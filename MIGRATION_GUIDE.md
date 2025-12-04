# Guía de Migración - Código Legacy a Arquitectura Profesional

Este documento explica la transformación del código original a la nueva arquitectura profesional.

## Resumen de Cambios

### Estructura Anterior (Legacy)

```
plate-cv/
├── old_code/                    # Código experimental sin organización
│   ├── fusion1.py
│   ├── fusion2.py
│   ├── binarizacionYcomConec.py
│   └── ...
├── src/
│   ├── recortador.py           # Scripts sueltos
│   └── generador_templates.py
├── Tests.ipynb                 # Notebook de pruebas
└── README.md
```

**Problemas**:
- Sin modularización
- Código duplicado
- Sin separación de responsabilidades
- Nombres poco descriptivos
- Difícil de mantener y extender

### Estructura Nueva (Profesional)

```
plate-cv/
├── src/plate_detector/              # Paquete profesional
│   ├── domain/                      # Capa de dominio (Clean Architecture)
│   │   ├── entities.py              # PlateRegion, BoundingBox, etc.
│   │   └── validators.py            # Reglas de negocio
│   ├── application/                 # Casos de uso
│   │   ├── plate_detection.py       # Servicio de detección
│   │   └── digit_extraction.py      # Servicio de extracción
│   ├── infrastructure/              # Implementaciones técnicas
│   │   ├── image_processing/
│   │   │   ├── binarization.py
│   │   │   ├── component_analysis.py
│   │   │   └── filters.py
│   │   └── template_matching/
│   │       └── generator.py
│   ├── interfaces/                  # Interfaces de entrada
│   │   └── cli.py                   # CLI profesional
│   └── config.py                    # Configuración centralizada
├── tests/                           # Tests unitarios
├── docs/                            # Documentación completa
├── examples/                        # Scripts de ejemplo
├── legacy/                          # Código antiguo (referencia)
├── notebooks/                       # Jupyter notebooks
└── requirements.txt, setup.py, etc.
```

**Mejoras**:
- Arquitectura limpia por capas
- Responsabilidad única
- Fácil de testear
- Extensible
- Documentación completa

## Mapeo de Código Legacy → Nuevo

### recortador.py → Múltiples módulos

**Antes** (`src/recortador.py`):
```python
def detector(imgColor, imagen, verbose):
    # 200+ líneas mezclando todo:
    # - Binarización
    # - Detección de componentes
    # - Filtros
    # - Validación
    # - Visualización
    pass
```

**Después** (modularizado):

1. **Binarización** → `infrastructure/image_processing/binarization.py`:
```python
class ImageBinarizer:
    def binarize(self, image: np.ndarray) -> np.ndarray:
        _, binary_image = cv2.threshold(image, self.threshold, 255, cv2.THRESH_BINARY)
        return binary_image
```

2. **Componentes** → `infrastructure/image_processing/component_analysis.py`:
```python
class ConnectedComponentAnalyzer:
    def find_components(self, binary_image: np.ndarray):
        return cv2.connectedComponentsWithStats(binary_image)
```

3. **Filtros** → `infrastructure/image_processing/filters.py`:
```python
class TransitionFilter:
    def count_transitions(self, binary_image: np.ndarray) -> int:
        # Lógica específica de transiciones
```

4. **Validación** → `domain/validators.py`:
```python
class AspectRatioValidator:
    def validate(self, bounding_box: BoundingBox) -> bool:
        return self.min_ratio <= bounding_box.aspect_ratio <= self.max_ratio
```

5. **Orquestación** → `application/plate_detection.py`:
```python
class PlateDetectionService:
    def detect(self, image: np.ndarray) -> DetectionResult:
        # Orquesta todos los componentes
        binary = self.binarizer.binarize(gray)
        components = self.analyzer.find_components(binary)
        filtered = self._filter_by_geometry(components)
        validated = self._validate_candidates(filtered)
        return DetectionResult(detected_plates=validated)
```

### generador_templates.py → digit_extraction.py

**Antes**:
```python
# Funciones sueltas, variables globales
class static_variables:
    contador = 0

def recortar_imagen(img, selec):
    # Hardcoded paths
    cv2.imwrite(f'/home/tom/universidad/plate-cv/resources/templates/...')
```

**Después**:
```python
# Clase con estado encapsulado
class DigitExtractionService:
    def extract_digits(self, plate_region: PlateRegion) -> List[DigitRegion]:
        # Lógica limpia, sin paths hardcodeados
        cropped = self._crop_plate_margins(binary_plate)
        digits = self._detect_digits(cropped)
        return digits

    def save_digit_images(self, digits: List[DigitRegion], output_dir: str):
        # Paths configurables
```

## Cómo Usar el Código Nuevo

### Antes (Legacy)

```bash
# Tenías que editar el código para cambiar la imagen
python src/recortador.py  # Hardcoded "../resources/examples/img0.jpg"
```

### Ahora (Profesional)

```bash
# CLI intuitiva
python -m plate_detector.interfaces.cli detect resources/examples/img0.jpg --show

# O programáticamente con configuración
from plate_detector import PlateDetectionService
from plate_detector.config import PlateDetectorConfig

config = PlateDetectorConfig.high_sensitivity()
detector = PlateDetectionService()
result = detector.detect(image)
```

## Nuevas Capacidades

### 1. Configuración Flexible

**Antes**: Valores hardcodeados en el código
```python
umbral_global = 150  # Cambiar requiere editar código
rango_cantidad_diferencias = (30, 90)
```

**Ahora**: Configuración centralizada
```python
config = PlateDetectorConfig()
config.binarization.threshold = 160  # Fácil de cambiar
config.transition_filter.min_normalized_transitions = 35.0

# O usar perfiles predefinidos
config = PlateDetectorConfig.high_sensitivity()
```

### 2. Validación de Dominio

**Antes**: Lógica mezclada
```python
if not (2.8 < relacion_aspecto < 5):
    labels[labels == label] = 0
```

**Ahora**: Validadores reutilizables
```python
validator = AspectRatioValidator(min_ratio=2.8, max_ratio=5.0)
if validator.validate(bounding_box):
    # Lógica de negocio
```

### 3. Resultados Estructurados

**Antes**: Print statements
```python
print("Número de objetos válidos:", len(nuevos_stats))
```

**Ahora**: Objetos tipados
```python
result: DetectionResult = detector.detect(image)
print(f"Detectadas {result.plate_count} patentes en {result.processing_time:.2f}s")

best_plate = result.get_best_plate()
print(f"Mejor detección con confianza: {best_plate.confidence:.2%}")
```

### 4. Testing

**Antes**: No había tests

**Ahora**: Tests estructurados
```python
# tests/test_entities.py
def test_bounding_box_area():
    bb = BoundingBox(x=0, y=0, width=120, height=40)
    assert bb.area == 4800

def test_plate_detection():
    detector = PlateDetectionService()
    result = detector.detect(test_image)
    assert result.success == True
```

## Retrocompatibilidad

El código legacy se mantiene en `legacy/` para referencia. Si necesitas usar la versión antigua:

```bash
# Código legacy (NO RECOMENDADO)
python legacy/fusion1.py
python legacy/binarizacionYcomConec.py
```

## Migración Paso a Paso

Si tienes código que usa la versión antigua:

### 1. Actualizar imports

**Antes**:
```python
import sys
sys.path.append('../')
from src.recortador import detector
```

**Ahora**:
```python
from plate_detector.application.plate_detection import PlateDetectionService
```

### 2. Actualizar llamadas

**Antes**:
```python
stats = detector(imgColor, imgGray, verbose=True)
```

**Ahora**:
```python
detector = PlateDetectionService()
result = detector.detect(image, verbose=True)
plates = result.detected_plates
```

### 3. Actualizar configuración

**Antes**: Editar variables en el código
```python
# Dentro de recortador.py
umbral_global = 150
rango_cantidad_diferencias = (30, 90)
```

**Ahora**: Usar configuración
```python
from plate_detector.infrastructure.image_processing import ImageBinarizer

binarizer = ImageBinarizer(threshold=150)
detector = PlateDetectionService(binarizer=binarizer)
```

## Beneficios de la Nueva Arquitectura

1. **Mantenibilidad**: Código organizado por responsabilidades
2. **Extensibilidad**: Fácil agregar nuevos algoritmos
3. **Testabilidad**: Cada componente se prueba independientemente
4. **Documentación**: Docs completas (README, arquitectura, API)
5. **Configurabilidad**: Sin hardcoding, todo configurable
6. **Reutilización**: Componentes modulares reutilizables
7. **Profesionalismo**: Estándares de la industria

## Soporte

Si tienes problemas migrando tu código:
- Consulta la [Guía de Usuario](docs/user_guide.md)
- Revisa los [ejemplos](examples/)
- Abre un issue en GitHub

## Próximos Pasos

1. Familiarízate con la nueva estructura leyendo `docs/architecture.md`
2. Prueba los ejemplos en `examples/`
3. Lee la referencia de API en `docs/api_reference.md`
4. Ejecuta los tests: `python tests/test_entities.py`
5. Empieza a usar la nueva API en tu código
