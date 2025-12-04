# Guía de Contribución

Gracias por tu interés en contribuir al proyecto Plate Detector. Este documento te guiará en el proceso de contribución.

## Código de Conducta

Este proyecto adhiere a un código de conducta de respeto mutuo. Al participar, se espera que mantengas un ambiente profesional y acogedor.

## Cómo Contribuir

### Reportar Bugs

Si encuentras un bug, por favor abre un issue en GitHub con:

1. **Descripción clara**: Explica qué esperabas y qué obtuviste
2. **Pasos para reproducir**: Describe cómo reproducir el problema
3. **Entorno**: Sistema operativo, versión de Python, versión de OpenCV
4. **Screenshots** (si aplica): Imágenes que muestren el problema
5. **Logs**: Salida del programa con `--verbose`

**Ejemplo**:
```
Título: No detecta patentes en imágenes con baja iluminación

Descripción:
El detector no encuentra patentes cuando la imagen tiene poca luz.

Pasos para reproducir:
1. Ejecutar: python -m plate_detector.interfaces.cli detect dark_image.jpg
2. Resultado: 0 patentes detectadas (esperaba 1)

Entorno:
- OS: Ubuntu 22.04
- Python: 3.10.5
- OpenCV: 4.8.0

Imagen adjunta: [dark_image.jpg]
```

### Sugerir Mejoras

Para sugerir nuevas funcionalidades:

1. Abre un issue con etiqueta "enhancement"
2. Describe el caso de uso
3. Explica cómo beneficiaría al proyecto
4. Propón una posible implementación (opcional)

### Pull Requests

#### Proceso

1. **Fork** el repositorio
2. **Crea una rama** desde `main`:
   ```bash
   git checkout -b feature/mi-funcionalidad
   ```
3. **Implementa** tus cambios
4. **Escribe tests** para tu código
5. **Ejecuta los tests** existentes:
   ```bash
   python -m pytest tests/
   ```
6. **Formatea** el código:
   ```bash
   black src/ tests/ examples/
   flake8 src/
   ```
7. **Commit** con mensajes descriptivos:
   ```bash
   git commit -m "feat: agregar soporte para patentes brasileñas"
   ```
8. **Push** a tu fork:
   ```bash
   git push origin feature/mi-funcionalidad
   ```
9. **Abre un Pull Request** en GitHub

#### Guía de Estilo

**Commits**:
Usa [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` Nueva funcionalidad
- `fix:` Corrección de bug
- `docs:` Cambios en documentación
- `refactor:` Refactorización sin cambiar funcionalidad
- `test:` Agregar o modificar tests
- `chore:` Cambios en build, dependencias, etc.

**Ejemplos**:
```bash
git commit -m "feat: agregar binarización adaptativa"
git commit -m "fix: corregir cálculo de transiciones"
git commit -m "docs: actualizar guía de usuario"
git commit -m "refactor: extraer lógica de validación a clase separada"
```

**Código Python**:

- Sigue [PEP 8](https://pep8.org/)
- Usa type hints en todas las funciones
- Docstrings en formato Google:
  ```python
  def detect(self, image: np.ndarray, verbose: bool = False) -> DetectionResult:
      """
      Detecta patentes en una imagen.

      Args:
          image: Imagen a procesar (RGB o escala de grises)
          verbose: Si True, muestra información de depuración

      Returns:
          DetectionResult con las patentes detectadas

      Raises:
          ValueError: Si la imagen es inválida
      """
      pass
  ```
- Nombres descriptivos (evita abreviaturas)
- Máximo 88 caracteres por línea (Black default)

**Arquitectura**:

- Respeta la arquitectura limpia del proyecto
- Nuevas funcionalidades deben tener:
  - Entidades en `domain/`
  - Lógica de negocio en `application/`
  - Implementaciones técnicas en `infrastructure/`
  - Interfaces en `interfaces/`
- No agregues dependencias del dominio hacia capas externas

#### Tests

Todo nuevo código debe incluir tests:

```python
# tests/test_mi_funcionalidad.py

def test_nueva_funcionalidad():
    """Test de la nueva funcionalidad."""
    # Arrange
    detector = PlateDetectionService()
    image = create_test_image()

    # Act
    result = detector.detect(image)

    # Assert
    assert result.success == True
    assert result.plate_count > 0
```

Ejecutar tests:
```bash
# Todos los tests
pytest tests/

# Un archivo específico
pytest tests/test_entities.py

# Con cobertura
pytest --cov=plate_detector tests/
```

## Estructura del Proyecto

```
plate-cv/
├── src/plate_detector/     # Código fuente
│   ├── domain/            # Entidades y reglas de negocio
│   ├── application/       # Casos de uso
│   ├── infrastructure/    # Implementaciones técnicas
│   └── interfaces/        # CLI, API
├── tests/                 # Tests unitarios
├── examples/              # Scripts de ejemplo
├── docs/                  # Documentación
└── resources/             # Datasets, templates
```

## Áreas de Contribución

### Fácil (Good First Issue)

- Agregar tests unitarios
- Mejorar documentación
- Agregar ejemplos de uso
- Corregir typos

### Intermedio

- Optimizar algoritmos existentes
- Agregar nuevos perfiles de configuración
- Mejorar manejo de errores
- Agregar logging estructurado

### Avanzado

- Implementar OCR de dígitos
- Portar a C/C++ para microcontroladores
- Agregar API REST
- Soporte para otros tipos de patentes (Brasil, Chile, etc.)
- Detección en video en tiempo real

## Preguntas Frecuentes

**¿Puedo trabajar en un issue que ya está asignado?**
No, espera a que esté libre o comenta para coordinarte con quien lo tiene asignado.

**¿Cuánto tiempo tardan en revisar mi PR?**
Generalmente 2-7 días. Si no hay respuesta en una semana, menciona a los maintainers.

**¿Debo abrir un issue antes de hacer un PR?**
Para features grandes sí, para fixes pequeños no es necesario.

**¿Puedo usar otra herramienta en vez de Black?**
No, para mantener consistencia usamos Black exclusivamente.

## Reconocimientos

Los contribuidores serán listados en el README.md. ¡Gracias por tu aporte!

## Licencia

Al contribuir, aceptas que tu código se distribuya bajo la licencia MIT del proyecto.
