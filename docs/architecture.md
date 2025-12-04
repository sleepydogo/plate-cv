# Arquitectura del Sistema

## Visión General

El sistema de detección de patentes está diseñado siguiendo los principios de **Clean Architecture** (Arquitectura Limpia) propuesta por Robert C. Martin, garantizando:

- **Independencia de frameworks**: El núcleo no depende de OpenCV o bibliotecas externas
- **Testabilidad**: Cada componente puede ser probado independientemente
- **Independencia de la UI**: La lógica de negocio no conoce la interfaz
- **Independencia de la base de datos**: Actualmente no usa BD, pero podría agregarse
- **Independencia de agentes externos**: Las reglas de negocio están aisladas

## Capas de la Arquitectura

```
┌─────────────────────────────────────────────────────────┐
│                    INTERFACES                           │
│  (CLI, Web API, GUI - Puntos de entrada del usuario)   │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                   APPLICATION                           │
│     (Casos de uso: PlateDetectionService, etc.)        │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                     DOMAIN                              │
│  (Entidades: PlateRegion, BoundingBox, Validators)     │
└────────────────────▲────────────────────────────────────┘
                     │
┌────────────────────┴────────────────────────────────────┐
│                 INFRASTRUCTURE                          │
│   (OpenCV, Procesamiento de Imágenes, I/O de archivos) │
└─────────────────────────────────────────────────────────┘
```

### 1. Capa de Dominio (`domain/`)

**Responsabilidad**: Contiene las reglas de negocio puras y entidades del sistema.

**Componentes**:

- **`entities.py`**: Define las entidades principales
  - `BoundingBox`: Representa un cuadro delimitador
  - `PlateRegion`: Región candidata de patente
  - `DigitRegion`: Región de un dígito individual
  - `DetectionResult`: Resultado completo de una detección

- **`validators.py`**: Validadores de reglas de negocio
  - `AspectRatioValidator`: Valida relación ancho/alto
  - `AreaValidator`: Valida relación de áreas
  - `TransitionValidator`: Valida transiciones de color
  - `PlateValidator`: Validador completo

**Principios**:
- Sin dependencias externas
- Lógica de negocio pura
- Inmutable cuando sea posible
- Testeable sin mocks

**Ejemplo**:
```python
@dataclass
class PlateRegion:
    bounding_box: BoundingBox
    confidence: float
    transitions_count: int

    @property
    def is_valid(self) -> bool:
        return self.confidence > 0.5
```

### 2. Capa de Aplicación (`application/`)

**Responsabilidad**: Implementa los casos de uso del sistema orquestando entidades y servicios de infraestructura.

**Componentes**:

- **`plate_detection.py`**: Servicio de detección de patentes
  - Pipeline completo de detección
  - Orquestación de filtros y validadores
  - Cálculo de confianza

- **`digit_extraction.py`**: Servicio de extracción de dígitos
  - Recorte de márgenes
  - Detección de caracteres individuales
  - Generación de templates

**Principios**:
- Coordina la lógica de negocio
- Usa inversión de dependencias (DI)
- Un caso de uso por clase
- Retorna entidades de dominio

**Ejemplo**:
```python
class PlateDetectionService:
    def __init__(self, binarizer, component_analyzer, ...):
        self.binarizer = binarizer
        self.component_analyzer = component_analyzer

    def detect(self, image: np.ndarray) -> DetectionResult:
        # Orquesta el pipeline completo
        pass
```

### 3. Capa de Infraestructura (`infrastructure/`)

**Responsabilidad**: Implementaciones técnicas usando bibliotecas externas (OpenCV).

**Componentes**:

**`image_processing/`**:
- `binarization.py`: Algoritmos de binarización
  - Umbral global
  - Umbral adaptativo
  - Método de Otsu

- `component_analysis.py`: Análisis de componentes conectados
  - Detección de componentes
  - Extracción de ROI
  - Dibujado de resultados

- `filters.py`: Filtros especializados
  - `TransitionFilter`: Análisis de transiciones
  - `MorphologicalFilter`: Erosión, dilatación, etc.
  - `EdgeDetector`: Detección de bordes (Canny)

**`template_matching/`**:
- `generator.py`: Generación de templates
  - Guardado de dígitos
  - Organización por etiquetas

**Principios**:
- Implementa interfaces del dominio
- Aislamiento de dependencias externas
- Fácilmente reemplazable (ej: OpenCV → otra lib)

### 4. Capa de Interfaces (`interfaces/`)

**Responsabilidad**: Puntos de entrada al sistema (CLI, API, GUI).

**Componentes**:

- **`cli.py`**: Interfaz de línea de comandos
  - Comando `detect`: Detectar patentes
  - Comando `extract`: Extraer dígitos
  - Parsing de argumentos

**Principios**:
- Adaptadores delgados
- Transforman input externo → llamadas a aplicación
- Formatean output para el usuario

## Flujo de Datos

### Detección de Patentes

```
Usuario → CLI.detect_command()
    ↓
PlateDetectionService.detect()
    ↓
1. ImageBinarizer.binarize()
2. ConnectedComponentAnalyzer.find_components()
3. Filtros geométricos (AspectRatio, Area)
4. TransitionFilter.count_transitions()
5. PlateValidator.validate_plate_region()
    ↓
DetectionResult (entidad de dominio)
    ↓
CLI formatea y muestra resultado
```

### Extracción de Dígitos

```
Usuario → CLI.extract_digits_command()
    ↓
PlateDetectionService.detect() [detectar patente primero]
    ↓
DigitExtractionService.extract_digits()
    ↓
1. Binarización de patente
2. Recorte de márgenes
3. Detección de componentes (dígitos)
4. Filtrado por área
    ↓
List[DigitRegion] (entidades de dominio)
    ↓
Guardado o visualización
```

## Inversión de Dependencias

El sistema usa **Dependency Injection** para mantener bajo acoplamiento:

```python
# ✓ Correcto: Inyección de dependencias
service = PlateDetectionService(
    binarizer=ImageBinarizer(threshold=150),
    component_analyzer=ConnectedComponentAnalyzer(),
    transition_filter=TransitionFilter(),
    validator=PlateValidator()
)

# ✗ Incorrecto: Dependencias hardcodeadas
class PlateDetectionService:
    def __init__(self):
        self.binarizer = ImageBinarizer()  # Acoplamiento fuerte
```

## Configuración Centralizada

La clase `PlateDetectorConfig` centraliza toda la configuración:

```python
@dataclass
class PlateDetectorConfig:
    binarization: BinarizationConfig
    geometric_filter: GeometricFilterConfig
    transition_filter: TransitionFilterConfig
    digit_extraction: DigitExtractionConfig
    visualization: VisualizationConfig
```

**Perfiles predefinidos**:
- `default()`: Configuración balanceada
- `high_sensitivity()`: Detecta más candidatos
- `high_precision()`: Menos falsos positivos

## Extensibilidad

### Agregar nuevo algoritmo de binarización

1. Crear método en `ImageBinarizer`:
```python
def binarize_with_custom(self, image):
    # Implementación
    return binary_image
```

2. Usar en `PlateDetectionService`:
```python
binary_image = self.binarizer.binarize_with_custom(gray_image)
```

### Agregar nueva interfaz (Web API)

1. Crear `interfaces/api.py`:
```python
from fastapi import FastAPI
from ..application.plate_detection import PlateDetectionService

app = FastAPI()

@app.post("/detect")
def detect_endpoint(image: UploadFile):
    detector = PlateDetectionService()
    result = detector.detect(image)
    return result.to_dict()
```

## Decisiones de Diseño

### ¿Por qué Clean Architecture?

- **Portabilidad**: Fácil migrar a C/C++ para microcontroladores
- **Testabilidad**: Cada capa se prueba independientemente
- **Mantenibilidad**: Cambios aislados, bajo impacto
- **Escalabilidad**: Agregar features sin romper existentes

### ¿Por qué Dataclasses?

- Inmutabilidad (usando `frozen=True` cuando corresponde)
- Type hints nativos
- Menos boilerplate que clases tradicionales
- Serialización sencilla

### ¿Por qué no usar herencia?

- Preferimos **composición sobre herencia**
- Evita jerarquías complejas
- Mayor flexibilidad en runtime
- Facilita el testing con mocks

## Testing

### Estructura de Tests

```
tests/
├── test_domain/
│   ├── test_entities.py
│   └── test_validators.py
├── test_application/
│   ├── test_plate_detection.py
│   └── test_digit_extraction.py
├── test_infrastructure/
│   ├── test_binarization.py
│   └── test_filters.py
└── test_integration/
    └── test_full_pipeline.py
```

### Ejemplo de Test

```python
def test_aspect_ratio_validator():
    validator = AspectRatioValidator(min_ratio=2.8, max_ratio=5.0)
    bb = BoundingBox(x=0, y=0, width=120, height=40)

    assert validator.validate(bb) == True  # 120/40 = 3.0
```

## Métricas de Calidad

- **Cobertura de código**: Objetivo > 80%
- **Complejidad ciclomática**: < 10 por función
- **Acoplamiento**: Bajo (medido con herramientas)
- **Cohesión**: Alta (responsabilidad única)

## Referencias

- [Clean Architecture - Robert C. Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Domain-Driven Design - Eric Evans](https://www.domainlanguage.com/ddd/)
- [SOLID Principles](https://en.wikipedia.org/wiki/SOLID)
