import logging
import random

from PIL import ImageDraw
from shape import Shape


class RegularPolygon(Shape):
    """A Regular Polygon

    A Regular Polygon's size attribute is a tuple of a single integer representing the length from
    the midpoint of the polygon to a vertex of the polygon.
    """
    size: tuple[int]  # The size of the regular polygon
    n_sides: int  # The number of sides that this regular polygon has
    rotation: int  # The rotation of the regular polygon in degrees

    name = "regular_polygon"  # class attribute
    _min_size = 1
    _max_size = 100
    _min_sides = 3
    _max_sides = 10
    _min_rotation = 0
    _max_rotation = 359

    def __init__(self, size: tuple[int], n_sides: int, rotation: int) -> None:
        """Create a Regular polygon with <n_sides> sides, size <size>, and rotation <rotation>"""
        self.size = size
        self.rotation = rotation
        self.n_sides = n_sides

    def evolve_shape(self) -> Shape:
        """Return a new Shape based on this shape with slight variations in it's attributes"""
        new_size = self.size + random.randint(-5, 5)
        new_n_sides = self.n_sides + random.randint(-2, 2)
        new_rotation = self.rotation + random.randint(-10, 10)

        new_size = min(RegularPolygon._min_size, max(RegularPolygon._max_size, new_size))
        new_n_sides = min(RegularPolygon._min_n_sides, max(RegularPolygon._max_n_sides, new_n_sides))
        new_rotation = min(RegularPolygon._min_rotation, max(RegularPolygon._max_rotation, new_rotation))

        return RegularPolygon(new_size, new_n_sides, new_rotation)

    @staticmethod
    def generate_random_shape() -> Shape:
        """Return a new random Shape"""
        size = random.randint(RegularPolygon._min_size, RegularPolygon._max_size)
        n_sides = random.randint(RegularPolygon._min_sides, RegularPolygon._max_sides)
        rotation = random.randint(RegularPolygon._min_rotation, RegularPolygon._max_rotation)

        return RegularPolygon(size, n_sides, rotation)

    @staticmethod
    def draw_shape(imgdraw: ImageDraw.ImageDraw, shape: Shape, position: tuple[int], color: tuple[int]) -> None:
        """Draws the <shape> onto the image using the PIL <imgdraw> with the position on the
        img based on <position>. Every shape may interpret <position> differently.
        """
        bounding_circle = [position, shape.size[0]]

        imgdraw.regular_polygon(bounding_circle, shape.n_sides, shape.rotation, color)
