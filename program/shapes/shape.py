from __future__ import annotations
from PIL import ImageDraw


class Shape:
    """Abstract class defining a shape used in the filter process

    Every Shape has an attribute for size

    Every Shape has methods that handle drawing the shape, evolving the shape,
    and generating a new random shape
    """
    name: str  # The type of or name of the shape
    size: tuple[int]  # The size of the shape

    def __init__(self) -> None:
        raise NotImplementedError()

    def evolve_shape(self) -> Shape:
        """Return a new Shape based on this shape with slight variations in it's attributes"""
        raise NotImplementedError()

    @staticmethod
    def generate_random_shape() -> Shape:
        """Return a new random Shape"""
        raise NotImplementedError()

    @staticmethod
    def draw_shape(imgdraw: ImageDraw.ImageDraw, shape: Shape, position: tuple[int], color: tuple[int]) -> None:
        """Draws the <shape> onto the image using the PIL <imgdraw> with the position on the
        img based on <position>. Every shape may interpret <position> differently.
        """
        raise NotImplementedError()
