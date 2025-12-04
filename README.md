# Plate Detector

Sistema profesional de detección de patentes argentinas usando procesamiento clásico de imágenes, diseñado para ejecutarse en microcontroladores y sistemas embebidos como Raspberry Pi.

![Patente Argentina](https://external-content.duckduckgo.com/iu/?u=http%3A%2F%2Fwpc.72c72.betacdn.net%2F8072C72%2Flvi-images%2Fsites%2Fdefault%2Ffiles%2Fstyles%2Flandscape_1020_560%2Fpublic%2Farticulo_patrocinado%2FSin-titulo-1_10.png&f=1&nofb=1&ipt=fb7adbc9646a75637bb5b48a56540f0e290600a77c7d179803e79bf669bd918c&ipo=images)

## Características

- **Procesamiento Clásico**: No requiere redes neuronales ni IA, ideal para sistemas con recursos limitados
- **Arquitectura Limpia**: Diseño modular basado en DDD (Domain-Driven Design)
- **Alto Rendimiento**: Optimizado para Raspberry Pi y microcontroladores
- **Configuración Flexible**: Múltiples perfiles de configuración (default, alta sensibilidad, alta precisión)
- **CLI Intuitiva**: Interfaz de línea de comandos fácil de usar
- **Extensible**: Arquitectura preparada para agregar nuevos algoritmos y funcionalidades

## Instalación

### Requisitos Previos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

### Instalación desde el código fuente

```bash
# Clonar el repositorio
git clone https://github.com/sleepydogo/plate-cv.git
cd plate-cv

# Crear entorno virtual (recomendado)
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Instalar el paquete en modo desarrollo
pip install -e .
```

## Uso Rápido

### Detectar patentes en una imagen

```bash
# Detección básica
python -m plate_detector.interfaces.cli detect imagen.jpg --show

# Detección con alta sensibilidad
python -m plate_detector.interfaces.cli detect imagen.jpg --config high_sensitivity --show

# Guardar resultado
python -m plate_detector.interfaces.cli detect imagen.jpg --output resultado.jpg
```

### Extraer dígitos de una patente

```bash
# Extraer y mostrar dígitos
python -m plate_detector.interfaces.cli extract imagen.jpg --show

# Guardar dígitos en un directorio
python -m plate_detector.interfaces.cli extract imagen.jpg --output ./digits/
```

### Uso programático

```python
import cv2
from plate_detector import PlateDetectionService

# Cargar imagen
image = cv2.imread("patente.jpg")

# Crear detector
detector = PlateDetectionService()

# Detectar patentes
result = detector.detect(image, verbose=True)

# Procesar resultados
if result.success:
    print(f"Patentes detectadas: {result.plate_count}")
    for plate in result.detected_plates:
        print(f"Confianza: {plate.confidence:.2%}")
        print(f"Posición: ({plate.bounding_box.x}, {plate.bounding_box.y})")

    # Mostrar resultado
    detector.display_result(result)
```

## Arquitectura

El proyecto sigue los principios de **Arquitectura Limpia** (Clean Architecture):

```
src/plate_detector/
├── domain/              # Entidades y reglas de negocio
│   ├── entities.py      # PlateRegion, DetectionResult, BoundingBox
│   └── validators.py    # Validadores de dominio
├── application/         # Casos de uso
│   ├── plate_detection.py
│   └── digit_extraction.py
├── infrastructure/      # Implementaciones técnicas
│   ├── image_processing/
│   │   ├── binarization.py
│   │   ├── component_analysis.py
│   │   └── filters.py
│   └── template_matching/
│       └── generator.py
├── interfaces/          # Interfaces de entrada (CLI, API)
│   └── cli.py
└── config.py           # Configuración centralizada
```

### Capas

1. **Dominio**: Entidades puras, sin dependencias externas
2. **Aplicación**: Lógica de negocio y casos de uso
3. **Infraestructura**: Implementaciones de OpenCV y procesamiento de imágenes
4. **Interfaces**: CLI, API REST (futura), etc.

## Algoritmo de Detección

El sistema utiliza un pipeline de procesamiento clásico:

1. **Binarización**: Conversión a imagen binaria con umbral ajustable
2. **Componentes Conectados**: Detección de regiones candidatas
3. **Filtros Geométricos**:
   - Relación de aspecto: 2.8 - 5.0 (ancho/alto)
   - Relación de área: 23 - 300 (área_total/área_componente)
4. **Filtro de Transiciones**: Análisis de cambios blanco-negro característicos de caracteres
5. **Validación Final**: Combinación de todos los criterios

## Configuración

### Perfiles Predefinidos

```python
from plate_detector.config import PlateDetectorConfig

# Configuración por defecto
config = PlateDetectorConfig.default()

# Alta sensibilidad (más detecciones, posibles falsos positivos)
config = PlateDetectorConfig.high_sensitivity()

# Alta precisión (menos falsos positivos, puede perder detecciones)
config = PlateDetectorConfig.high_precision()
```

### Personalización

```python
config = PlateDetectorConfig()
config.binarization.threshold = 160
config.geometric_filter.min_aspect_ratio = 3.0
config.transition_filter.min_normalized_transitions = 35.0
config.verbose = True
```

## Estructura del Proyecto

```
plate-cv/
├── src/                     # Código fuente
│   └── plate_detector/      # Paquete principal
├── tests/                   # Tests unitarios
├── docs/                    # Documentación técnica
├── resources/               # Recursos (datasets, templates, ejemplos)
│   ├── datasets/
│   ├── templates/
│   └── examples/
├── notebooks/               # Jupyter notebooks de análisis
├── legacy/                  # Código legacy (referencia)
├── requirements.txt         # Dependencias
├── setup.py                # Configuración de instalación
└── README.md               # Este archivo
```

## Desarrollo

### Ejecutar tests

```bash
# Instalar dependencias de desarrollo
pip install -e ".[dev]"

# Ejecutar tests
pytest tests/
```

### Formateo de código

```bash
# Formatear con Black
black src/

# Verificar con flake8
flake8 src/
```

## Roadmap

- [ ] Tests unitarios completos
- [ ] Soporte para reconocimiento OCR de dígitos
- [ ] API REST para detección remota
- [ ] Optimización para microcontroladores (C/C++)
- [ ] Soporte para patentes de otros países
- [ ] Interfaz web (frontend)

## Recursos Educativos

- [Documentación Técnica](docs/architecture.md)
- [Guía del Usuario](docs/user_guide.md)
- [Referencia de API](docs/api_reference.md)
- [Notebook de Desarrollo](notebooks/development_process.ipynb)

## Contribuir

Las contribuciones son bienvenidas. Por favor:

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## Contacto

Tom - [@sleepydogo](https://github.com/sleepydogo)

Project Link: [https://github.com/sleepydogo/plate-cv](https://github.com/sleepydogo/plate-cv)

## Agradecimientos

- Proyecto desarrollado como parte de investigación en visión por computadora
- Basado en técnicas clásicas de procesamiento de imágenes
- Optimizado para sistemas embebidos y microcontroladores
