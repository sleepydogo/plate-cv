"""
Configuración centralizada del sistema de detección de patentes.
"""

from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class BinarizationConfig:
    """Configuración de binarización."""

    threshold: int = 150
    use_adaptive: bool = False
    adaptive_block_size: int = 11
    adaptive_constant: int = 2


@dataclass
class GeometricFilterConfig:
    """Configuración de filtros geométricos."""

    # Relación de aspecto (ancho/alto)
    min_aspect_ratio: float = 2.8
    max_aspect_ratio: float = 5.0

    # Relación de área (área_total/área_componente)
    min_area_ratio: float = 23.0
    max_area_ratio: float = 300.0


@dataclass
class TransitionFilterConfig:
    """Configuración del filtro de transiciones."""

    # Proporciones verticales donde analizar transiciones
    proportions: List[float] = None

    # Rango de transiciones normalizadas aceptables
    min_normalized_transitions: float = 30.0
    max_normalized_transitions: float = 90.0

    def __post_init__(self):
        if self.proportions is None:
            self.proportions = [0.25, 0.5, 0.75]


@dataclass
class DigitExtractionConfig:
    """Configuración de extracción de dígitos."""

    binarization_threshold: int = 140
    margin_intensity_threshold: int = 100
    margin_bottom_rows: int = 15

    # Factores para calcular área de dígitos
    max_area_divisor: float = 6.0
    min_area_divisor: float = 62.0


@dataclass
class VisualizationConfig:
    """Configuración de visualización."""

    window_size: Tuple[int, int] = (700, 700)
    bounding_box_color: Tuple[int, int, int] = (0, 255, 0)  # Verde en BGR
    bounding_box_thickness: int = 2
    show_confidence: bool = True


@dataclass
class PlateDetectorConfig:
    """Configuración completa del sistema."""

    binarization: BinarizationConfig = None
    geometric_filter: GeometricFilterConfig = None
    transition_filter: TransitionFilterConfig = None
    digit_extraction: DigitExtractionConfig = None
    visualization: VisualizationConfig = None

    # Configuración general
    verbose: bool = False
    save_intermediate_results: bool = False

    def __post_init__(self):
        # Inicializar sub-configuraciones si no existen
        if self.binarization is None:
            self.binarization = BinarizationConfig()
        if self.geometric_filter is None:
            self.geometric_filter = GeometricFilterConfig()
        if self.transition_filter is None:
            self.transition_filter = TransitionFilterConfig()
        if self.digit_extraction is None:
            self.digit_extraction = DigitExtractionConfig()
        if self.visualization is None:
            self.visualization = VisualizationConfig()

    @classmethod
    def default(cls) -> "PlateDetectorConfig":
        """
        Retorna la configuración por defecto optimizada para patentes argentinas.

        Esta configuración está ajustada según los valores encontrados
        en el código original.
        """
        return cls()

    @classmethod
    def high_sensitivity(cls) -> "PlateDetectorConfig":
        """
        Configuración de alta sensibilidad (detecta más candidatos).

        Útil cuando las condiciones de iluminación son variables.
        """
        config = cls()
        config.geometric_filter.max_area_ratio = 400.0
        config.transition_filter.min_normalized_transitions = 25.0
        config.transition_filter.max_normalized_transitions = 100.0
        return config

    @classmethod
    def high_precision(cls) -> "PlateDetectorConfig":
        """
        Configuración de alta precisión (menos falsos positivos).

        Útil cuando se necesita máxima certeza en las detecciones.
        """
        config = cls()
        config.geometric_filter.min_aspect_ratio = 3.0
        config.geometric_filter.max_aspect_ratio = 4.5
        config.transition_filter.min_normalized_transitions = 40.0
        config.transition_filter.max_normalized_transitions = 80.0
        return config

    def to_dict(self) -> dict:
        """Convierte la configuración a un diccionario."""
        return {
            "binarization": self.binarization.__dict__,
            "geometric_filter": self.geometric_filter.__dict__,
            "transition_filter": self.transition_filter.__dict__,
            "digit_extraction": self.digit_extraction.__dict__,
            "visualization": self.visualization.__dict__,
            "verbose": self.verbose,
            "save_intermediate_results": self.save_intermediate_results,
        }


# Constantes del sistema
SUPPORTED_IMAGE_FORMATS = [".jpg", ".jpeg", ".png", ".bmp", ".tiff"]
DEFAULT_OUTPUT_DIR = "output"
DEFAULT_TEMPLATE_DIR = "resources/templates"
DEFAULT_DATASET_DIR = "resources/datasets"
