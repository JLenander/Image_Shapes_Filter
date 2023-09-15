import logging
import random

from PIL import ImageDraw
from shapes.shape import Shape
from shapes.regular_polygon import RegularPolygon


class Square(RegularPolygon):
    """A Square

    A Square's size attribute is a tuple of one integer representing the length of the square
    """
    name = "Square"  # class attribute
    _min_size = 1
    _max_size = 100
    _min_rotation = 0
    _max_rotation = 359

    def __init__(self, size: tuple[int], rotation: int) -> None:
        """Create a Square with size <size> and rotation <rotation>"""
        self.size = size
        self.rotation = rotation
        self.n_sides = 4

    def evolve_shape(self) -> Shape:
        """Return a new Shape based on this shape with slight variations in it's attributes"""
        new_size = self.size[0] + random.randint(-5, 5)
        new_rotation = self.rotation + random.randint(-10, 10)

        new_size = min(Square._min_size, max(Square._max_size, new_size))
        new_rotation = min(Square._min_rotation, max(Square._max_rotation, new_rotation))

        return Square((new_size,), new_rotation)

    @staticmethod
    def generate_random_shape() -> Shape:
        """Return a new random Shape using <target> as a reference for color"""
        size = random.randint(Square._min_size, Square._max_size)
        rotation = random.randint(Square._min_rotation, Square._max_rotation)

        return Square((size,), rotation)

    @staticmethod
    def draw_shape(imgdraw: ImageDraw.ImageDraw, shape: Shape, position: tuple[int], color: tuple[int]) -> None:
        """Draws the <shape> onto the image using the PIL <imgdraw> with the position on the
        img based on <position>. Every shape may interpret <position> differently.
        """
        RegularPolygon.draw_shape(imgdraw, shape, position, color)
