"""
Validadores de dominio para regiones de patentes.
"""

from typing import Tuple
from .entities import BoundingBox, PlateRegion


class AspectRatioValidator:
    """Valida la relación de aspecto de una región candidata."""

    def __init__(self, min_ratio: float = 2.8, max_ratio: float = 5.0):
        """
        Args:
            min_ratio: Relación de aspecto mínima aceptable
            max_ratio: Relación de aspecto máxima aceptable
        """
        self.min_ratio = min_ratio
        self.max_ratio = max_ratio

    def validate(self, bounding_box: BoundingBox) -> bool:
        """
        Valida si la relación de aspecto está dentro del rango permitido.

        Args:
            bounding_box: Cuadro delimitador a validar

        Returns:
            True si la relación de aspecto es válida
        """
        aspect_ratio = bounding_box.aspect_ratio
        return self.min_ratio <= aspect_ratio <= self.max_ratio

    def __repr__(self) -> str:
        return f"AspectRatioValidator(min={self.min_ratio}, max={self.max_ratio})"


class AreaValidator:
    """Valida el área de una región en relación con el área total."""

    def __init__(self, min_area_ratio: float = 23.0, max_area_ratio: float = 300.0):
        """
        Args:
            min_area_ratio: Relación mínima área_total/área_componente
            max_area_ratio: Relación máxima área_total/área_componente
        """
        self.min_area_ratio = min_area_ratio
        self.max_area_ratio = max_area_ratio

    def validate(self, bounding_box: BoundingBox, total_area: int) -> bool:
        """
        Valida si el área está dentro del rango permitido.

        Args:
            bounding_box: Cuadro delimitador a validar
            total_area: Área total de la imagen

        Returns:
            True si la relación de área es válida
        """
        if bounding_box.area == 0:
            return False

        area_ratio = total_area / bounding_box.area
        return self.min_area_ratio <= area_ratio <= self.max_area_ratio

    def __repr__(self) -> str:
        return f"AreaValidator(min={self.min_area_ratio}, max={self.max_area_ratio})"


class TransitionValidator:
    """Valida las transiciones de color en una región (cambios blanco-negro)."""

    def __init__(self, min_transitions: int = 30, max_transitions: int = 90):
        """
        Args:
            min_transitions: Número mínimo de transiciones normalizadas
            max_transitions: Número máximo de transiciones normalizadas
        """
        self.min_transitions = min_transitions
        self.max_transitions = max_transitions

    def validate(self, normalized_transitions: float) -> bool:
        """
        Valida si el número de transiciones está dentro del rango.

        Las patentes tienen múltiples caracteres, lo que genera
        transiciones de color características.

        Args:
            normalized_transitions: Valor de transiciones normalizado

        Returns:
            True si las transiciones están en el rango válido
        """
        return self.min_transitions <= normalized_transitions <= self.max_transitions

    def __repr__(self) -> str:
        return f"TransitionValidator(min={self.min_transitions}, max={self.max_transitions})"


class PlateValidator:
    """Validador completo que combina múltiples criterios."""

    def __init__(
        self,
        aspect_ratio_validator: AspectRatioValidator = None,
        area_validator: AreaValidator = None,
        transition_validator: TransitionValidator = None,
    ):
        """
        Inicializa el validador con validadores específicos.
        Si no se proveen, usa los valores por defecto.
        """
        self.aspect_ratio_validator = aspect_ratio_validator or AspectRatioValidator()
        self.area_validator = area_validator or AreaValidator()
        self.transition_validator = transition_validator or TransitionValidator()

    def validate_plate_region(
        self, plate: PlateRegion, total_image_area: int
    ) -> Tuple[bool, str]:
        """
        Valida una región de patente completa.

        Args:
            plate: Región de patente a validar
            total_image_area: Área total de la imagen

        Returns:
            Tupla (es_válida, mensaje_error)
        """
        # Validar aspecto
        if not self.aspect_ratio_validator.validate(plate.bounding_box):
            return False, "Relación de aspecto inválida"

        # Validar área
        if not self.area_validator.validate(plate.bounding_box, total_image_area):
            return False, "Relación de área inválida"

        # Validar transiciones
        normalized_transitions = plate.get_normalized_transition_value()
        if not self.transition_validator.validate(normalized_transitions):
            return False, "Número de transiciones inválido"

        return True, "Válido"
