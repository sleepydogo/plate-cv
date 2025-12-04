"""
Módulo de procesamiento de imágenes.
"""

from .binarization import ImageBinarizer
from .component_analysis import ConnectedComponentAnalyzer
from .filters import TransitionFilter

__all__ = [
    "ImageBinarizer",
    "ConnectedComponentAnalyzer",
    "TransitionFilter",
]
