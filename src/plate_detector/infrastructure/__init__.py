"""
Capa de infraestructura - Implementaciones técnicas de procesamiento.
"""

from .image_processing.binarization import ImageBinarizer
from .image_processing.component_analysis import ConnectedComponentAnalyzer
from .image_processing.filters import TransitionFilter
from .template_matching.generator import TemplateGenerator

__all__ = [
    "ImageBinarizer",
    "ConnectedComponentAnalyzer",
    "TransitionFilter",
    "TemplateGenerator",
]
