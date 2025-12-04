# Referencia de API - Plate Detector

## Tabla de Contenidos

- [Domain Layer](#domain-layer)
  - [Entities](#entities)
  - [Validators](#validators)
- [Application Layer](#application-layer)
  - [PlateDetectionService](#platedetectionservice)
  - [DigitExtractionService](#digitextractionservice)
- [Infrastructure Layer](#infrastructure-layer)
  - [Image Processing](#image-processing)
  - [Template Matching](#template-matching)
- [Configuration](#configuration)

---

## Domain Layer

### Entities

#### BoundingBox

Representa un cuadro delimitador rectangular.

```python
from plate_detector.domain.entities import BoundingBox

bb = BoundingBox(x=100, y=50, width=120, height=40)
```

**Atributos**:
- `x: int` - Coordenada X superior izquierda
- `y: int` - Coordenada Y superior izquierda
- `width: int` - Ancho del cuadro
- `height: int` - Alto del cuadro

**Propiedades**:
- `area: int` - Área del cuadro (width × height)
- `aspect_ratio: float` - Relación de aspecto (width / height)
- `coordinates: Tuple[int, int, int, int]` - (x, y, x+w, y+h)

**Métodos**:
```python
contains_point(x: int, y: int) -> bool
```
Verifica si un punto está dentro del bounding box.

---

#### PlateRegion

Representa una región candidata de patente detectada.

```python
from plate_detector.domain.entities import PlateRegion, BoundingBox

plate = PlateRegion(
    bounding_box=BoundingBox(100, 50, 120, 40),
    confidence=0.85,
    transitions_count=450,
    image_data=roi_image  # opcional
)
```

**Atributos**:
- `bounding_box: BoundingBox` - Ubicación de la patente
- `confidence: float` - Confianza de detección (0.0-1.0)
- `transitions_count: int` - Número de transiciones detectadas
- `image_data: Optional[np.ndarray]` - Datos de imagen de la región
- `digits: List[DigitRegion]` - Lista de dígitos detectados

**Propiedades**:
- `is_valid: bool` - True si confidence > 0.5

**Métodos**:
```python
add_digit(digit: DigitRegion) -> None
get_normalized_transition_value() -> float
```

---

#### DigitRegion

Representa una región que contiene un dígito individual.

```python
from plate_detector.domain.entities import DigitRegion, BoundingBox

digit = DigitRegion(
    bounding_box=BoundingBox(10, 5, 15, 25),
    confidence=0.9,
    recognized_digit="A"  # opcional
)
```

**Atributos**:
- `bounding_box: BoundingBox` - Ubicación del dígito
- `image_data: Optional[np.ndarray]` - Imagen del dígito
- `confidence: float` - Confianza de detección
- `recognized_digit: Optional[str]` - Dígito reconocido (si aplica)

**Métodos**:
```python
extract_roi(source_image: np.ndarray) -> np.ndarray
```

---

#### DetectionResult

Resultado completo de la detección de patentes.

```python
from plate_detector.domain.entities import DetectionResult

result = DetectionResult(
    original_image=image,
    processed_image=annotated_image,
    detected_plates=[plate1, plate2],
    processing_time=0.123,
    success=True
)
```

**Atributos**:
- `original_image: np.ndarray` - Imagen original
- `processed_image: Optional[np.ndarray]` - Imagen con detecciones dibujadas
- `detected_plates: List[PlateRegion]` - Patentes detectadas
- `processing_time: float` - Tiempo de procesamiento en segundos
- `success: bool` - True si la detección fue exitosa
- `error_message: Optional[str]` - Mensaje de error (si aplica)

**Propiedades**:
- `plate_count: int` - Número de patentes detectadas

**Métodos**:
```python
get_best_plate() -> Optional[PlateRegion]
get_all_bounding_boxes() -> List[BoundingBox]
```

---

### Validators

#### AspectRatioValidator

Valida la relación de aspecto de una región.

```python
from plate_detector.domain.validators import AspectRatioValidator

validator = AspectRatioValidator(min_ratio=2.8, max_ratio=5.0)
is_valid = validator.validate(bounding_box)
```

**Constructor**:
- `min_ratio: float = 2.8` - Relación mínima
- `max_ratio: float = 5.0` - Relación máxima

**Métodos**:
```python
validate(bounding_box: BoundingBox) -> bool
```

---

#### AreaValidator

Valida el área de una región en relación con el área total.

```python
from plate_detector.domain.validators import AreaValidator

validator = AreaValidator(min_area_ratio=23.0, max_area_ratio=300.0)
is_valid = validator.validate(bounding_box, total_area=211455)
```

**Constructor**:
- `min_area_ratio: float = 23.0`
- `max_area_ratio: float = 300.0`

**Métodos**:
```python
validate(bounding_box: BoundingBox, total_area: int) -> bool
```

---

#### TransitionValidator

Valida las transiciones de color en una región.

```python
from plate_detector.domain.validators import TransitionValidator

validator = TransitionValidator(min_transitions=30, max_transitions=90)
is_valid = validator.validate(normalized_transitions=55.3)
```

**Constructor**:
- `min_transitions: int = 30`
- `max_transitions: int = 90`

**Métodos**:
```python
validate(normalized_transitions: float) -> bool
```

---

#### PlateValidator

Validador completo que combina múltiples criterios.

```python
from plate_detector.domain.validators import PlateValidator

validator = PlateValidator()
is_valid, message = validator.validate_plate_region(plate, total_image_area)
```

**Métodos**:
```python
validate_plate_region(
    plate: PlateRegion,
    total_image_area: int
) -> Tuple[bool, str]
```

Retorna tupla `(es_válida, mensaje_error)`.

---

## Application Layer

### PlateDetectionService

Servicio principal de detección de patentes.

```python
from plate_detector.application.plate_detection import PlateDetectionService

detector = PlateDetectionService()
result = detector.detect(image, verbose=True)
```

**Constructor**:
```python
PlateDetectionService(
    binarizer: Optional[ImageBinarizer] = None,
    component_analyzer: Optional[ConnectedComponentAnalyzer] = None,
    transition_filter: Optional[TransitionFilter] = None,
    validator: Optional[PlateValidator] = None
)
```

**Métodos**:

#### detect()
```python
detect(image: np.ndarray, verbose: bool = False) -> DetectionResult
```

Detecta patentes en una imagen.

**Parámetros**:
- `image: np.ndarray` - Imagen a procesar (RGB o escala de grises)
- `verbose: bool` - Si True, muestra información de depuración

**Retorna**: `DetectionResult`

**Ejemplo**:
```python
import cv2

image = cv2.imread("patente.jpg")
result = detector.detect(image, verbose=True)

if result.success:
    print(f"Detectadas {result.plate_count} patentes")
```

---

#### display_result()
```python
display_result(result: DetectionResult, window_size: tuple = (700, 700))
```

Muestra el resultado de la detección en una ventana.

**Parámetros**:
- `result: DetectionResult` - Resultado a mostrar
- `window_size: tuple` - Tamaño de ventana (ancho, alto)

---

### DigitExtractionService

Servicio para extraer dígitos individuales de patentes.

```python
from plate_detector.application.digit_extraction import DigitExtractionService

extractor = DigitExtractionService()
digits = extractor.extract_digits(plate_region, verbose=True)
```

**Constructor**:
```python
DigitExtractionService(
    binarizer: Optional[ImageBinarizer] = None,
    component_analyzer: Optional[ConnectedComponentAnalyzer] = None
)
```

**Métodos**:

#### extract_digits()
```python
extract_digits(
    plate_region: PlateRegion,
    verbose: bool = False
) -> List[DigitRegion]
```

Extrae los dígitos individuales de una región de patente.

**Parámetros**:
- `plate_region: PlateRegion` - Región de patente detectada
- `verbose: bool` - Modo verbose

**Retorna**: `List[DigitRegion]`

---

#### save_digit_images()
```python
save_digit_images(
    digit_regions: List[DigitRegion],
    output_dir: str,
    prefix: str = "digit"
) -> List[str]
```

Guarda las imágenes de los dígitos en archivos.

**Parámetros**:
- `digit_regions: List[DigitRegion]` - Lista de dígitos
- `output_dir: str` - Directorio de salida
- `prefix: str` - Prefijo para nombres de archivo

**Retorna**: Lista de rutas de archivos guardados

---

#### visualize_digits()
```python
visualize_digits(digit_regions: List[DigitRegion]) -> None
```

Visualiza los dígitos detectados en ventanas separadas.

---

## Infrastructure Layer

### Image Processing

#### ImageBinarizer

Realiza binarización de imágenes.

```python
from plate_detector.infrastructure.image_processing import ImageBinarizer

binarizer = ImageBinarizer(threshold=150)
binary_image = binarizer.binarize(gray_image)
```

**Constructor**:
- `threshold: int = 150` - Umbral de binarización (0-255)

**Métodos**:

##### binarize()
```python
binarize(image: np.ndarray) -> np.ndarray
```

Binariza una imagen usando umbral global.

---

##### adaptive_binarize()
```python
adaptive_binarize(
    image: np.ndarray,
    block_size: int = 11,
    c: int = 2
) -> np.ndarray
```

Binarización adaptativa usando umbral local.

---

##### binarize_with_otsu()
```python
binarize_with_otsu(image: np.ndarray) -> Tuple[np.ndarray, int]
```

Binariza usando el método de Otsu (umbral automático).

**Retorna**: Tupla `(imagen_binarizada, umbral_calculado)`

---

#### ConnectedComponentAnalyzer

Analiza componentes conectados en imágenes binarias.

```python
from plate_detector.infrastructure.image_processing import ConnectedComponentAnalyzer

analyzer = ConnectedComponentAnalyzer()
labels, stats, boxes = analyzer.find_components(binary_image)
```

**Métodos**:

##### find_components()
```python
find_components(
    binary_image: np.ndarray
) -> Tuple[np.ndarray, np.ndarray, List[BoundingBox]]
```

Encuentra componentes conectados.

**Retorna**: Tupla `(labels, stats, bounding_boxes)`

---

##### extract_roi()
```python
extract_roi(image: np.ndarray, bounding_box: BoundingBox) -> np.ndarray
```

Extrae una región de interés de la imagen.

---

##### draw_bounding_boxes()
```python
draw_bounding_boxes(
    image: np.ndarray,
    bounding_boxes: List[BoundingBox],
    color: Tuple[int, int, int] = (0, 255, 0),
    thickness: int = 2
) -> np.ndarray
```

Dibuja bounding boxes en una imagen.

---

#### TransitionFilter

Filtro basado en transiciones de color.

```python
from plate_detector.infrastructure.image_processing import TransitionFilter

filter = TransitionFilter(proportions=[0.25, 0.5, 0.75])
transitions = filter.count_transitions(binary_image)
```

**Constructor**:
- `proportions: List[float] = [0.25, 0.5, 0.75]` - Proporciones verticales donde analizar

**Métodos**:

##### count_transitions()
```python
count_transitions(binary_image: np.ndarray) -> int
```

Cuenta las transiciones de color en proporciones específicas.

---

##### get_normalized_transitions()
```python
get_normalized_transitions(binary_image: np.ndarray, width: int) -> float
```

Obtiene el valor de transiciones normalizado por el ancho.

---

## Configuration

### PlateDetectorConfig

Configuración centralizada del sistema.

```python
from plate_detector.config import PlateDetectorConfig

# Configuración por defecto
config = PlateDetectorConfig.default()

# Alta sensibilidad
config = PlateDetectorConfig.high_sensitivity()

# Alta precisión
config = PlateDetectorConfig.high_precision()
```

**Atributos**:
- `binarization: BinarizationConfig`
- `geometric_filter: GeometricFilterConfig`
- `transition_filter: TransitionFilterConfig`
- `digit_extraction: DigitExtractionConfig`
- `visualization: VisualizationConfig`
- `verbose: bool = False`
- `save_intermediate_results: bool = False`

**Métodos**:

##### default()
```python
@classmethod
default(cls) -> PlateDetectorConfig
```

Configuración por defecto optimizada para patentes argentinas.

---

##### high_sensitivity()
```python
@classmethod
high_sensitivity(cls) -> PlateDetectorConfig
```

Configuración de alta sensibilidad (detecta más candidatos).

---

##### high_precision()
```python
@classmethod
high_precision(cls) -> PlateDetectorConfig
```

Configuración de alta precisión (menos falsos positivos).

---

##### to_dict()
```python
to_dict() -> dict
```

Convierte la configuración a un diccionario.

---

## Ejemplos de Uso Completo

### Pipeline completo de detección

```python
import cv2
from plate_detector import PlateDetectionService
from plate_detector.application.digit_extraction import DigitExtractionService

# 1. Cargar imagen
image = cv2.imread("patente.jpg")

# 2. Detectar patente
detector = PlateDetectionService()
result = detector.detect(image, verbose=True)

if result.success:
    # 3. Obtener mejor patente
    best_plate = result.get_best_plate()
    print(f"Confianza: {best_plate.confidence:.2%}")

    # 4. Extraer dígitos
    extractor = DigitExtractionService()
    digits = extractor.extract_digits(best_plate)

    # 5. Guardar resultados
    extractor.save_digit_images(digits, "./output/")
    cv2.imwrite("resultado.jpg", result.processed_image)
```

### Configuración personalizada completa

```python
from plate_detector.config import PlateDetectorConfig
from plate_detector.application.plate_detection import PlateDetectionService

# Crear configuración personalizada
config = PlateDetectorConfig()
config.binarization.threshold = 160
config.geometric_filter.min_aspect_ratio = 3.0
config.transition_filter.min_normalized_transitions = 35.0
config.verbose = True

# Crear servicios con configuración
from plate_detector.infrastructure.image_processing import ImageBinarizer
binarizer = ImageBinarizer(threshold=config.binarization.threshold)

detector = PlateDetectionService(binarizer=binarizer)
result = detector.detect(image)
```
