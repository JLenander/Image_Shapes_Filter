"""Objects for selection of shape to use in filter.
Handles evolution of shapes.
"""

from PIL import ImageDraw, Image
from program.color_utils import average_color
import random


class shape_selector():
    """Base Shape Selector class"""

    def __init__(self) -> None:
        raise NotImplementedError()

    def random_shape(self, target: Image.Image) -> str:
        """Return a new random shape represented by a string using <target> as reference"""
        raise NotImplementedError()

    def random_shapes(self, target: Image.Image, n: int) -> list[str]:
        """Return a list of <n> new random shape strings using <target> as reference"""
        raise NotImplementedError()

    @staticmethod
    def draw_shape(img: Image.Image, shape_string: str) -> None:
        """Draw the shape described by unique <shape_string> on <img>"""
        raise NotImplementedError()


class random_shape_selector(shape_selector):
    """Shape Selector randomly selecting from available shapes using the pillow draw library

    Shapes:
        - ellipse (including circle)
        - rectangle (including square)

    Randomized Properties of Shapes:
        - diameter/width/height/length
        - location
    """
    bbox: list[int]  # list of points in the form [x0, y0, x1, y1]
    min_size: int  # Minimum diameter/dimensions of shape in pixels
    max_size: int  # Maximum diameter/dimensions of shape in pixels

    def __init__(self, bbox: list[tuple[int]] | list[int], min_size: int, max_size: int) -> None:
        """Initialize a new random_shape_selector object

        <bbox> is a list of two points in the form [(x0, y0), (x1, y1)] or the form [x0, y0, x1, y1]
        that define the bounding box for generated shapes. Bounding Box should be within the image.
        The points should be such that x0 < x1 and y0 < y1 (topleft point first then bottomright)

        <min_size> is the minimum diameter/width/height/length of the shape in pixels
        <max_size> is the maximum diameter/width/height/length of the shape in pixels

        requirements:
            - 0 < min_size < max_size
            - min_size < (x1 - x0)
            - min_size < (y1 - y0)
        """
        x0, y0, x1, y1 = -1, -1, -1, -1
        if isinstance(bbox[0], tuple):
            try:
                p1, p2 = bbox
                x0, y0 = p1
                x1, y1 = p2
            except ValueError:
                raise ValueError('Invalid 2-tuple bounding box format')
        else:
            try:
                x0, y0, x1, y1 = bbox
            except ValueError:
                raise ValueError('Invalid 4-int bounding box tuple format')
        if x0 >= x1 or y0 >= y1:
            raise ValueError('Invalid bounding box, point x0 should be < x1 and y0 should be < y1')
        self.bbox = [x0, y0, x1, y1]

        if min_size >= max_size:
            raise ValueError('min_size is not less than max_size')
        if min_size <= 0:
            raise ValueError('min_size must be at least 1 pixel')
        if min_size >= (x1 - x0) or min_size >= (y1 - y0):
            raise ValueError('min_size must be containable in the bounding box')
        self.min_size = min_size
        self.max_size = max_size

    def random_shape(self, target: Image.Image) -> str:
        """Return a new random shape represented by a string using <target> as reference

        Shape is contained within the bounding box defined by self.bbox

        String is delimited by ':' and has the following fields
            - shape
            - xy coordinates (coords defining shape for polygons or bbox for ellipse)
            - RGB color (generated by average color of the same region in <target>)
        """
        shapes = ['ellipse', 'rectangle']
        x0, y0, x1, y1 = self.bbox

        xy = []
        fill = ()
        shape = random.choice(shapes)
        match shape:
            case 'ellipse':
                # The bounding box topleft point x and y coordinates
                p1x = random.randrange(x0, x1 - self.min_size)
                p1y = random.randrange(y0, y1 - self.min_size)

                # The bounding box bottomright point x and y coordinates
                p2x = random.randrange(p1x + self.min_size, min(x1, p1x + self.max_size))
                p2y = random.randrange(p1y + self.min_size, min(y1, p1y + self.max_size))

                xy = [(p1x, p1y), (p2x, p2y)]

                # Use mask to determine average color of the region in the target
                mask = Image.new('1', target.size)
                mask_draw = ImageDraw.Draw(mask)
                mask_draw.ellipse(xy, 1)
                fill = average_color(target, mask)
            case 'rectangle':
                # The bounding box topleft point x and y coordinates
                p1x = random.randrange(x0, x1 - self.min_size)
                p1y = random.randrange(y0, y1 - self.min_size)

                # The bounding box bottomright point x and y coordinates
                p2x = random.randrange(p1x + self.min_size, min(x1, p1x + self.max_size))
                p2y = random.randrange(p1y + self.min_size, min(y1, p1y + self.max_size))

                xy = [(p1x, p1y), (p2x, p2y)]

                # Use mask to determine average color of the region in the target
                mask = Image.new('1', target.size)
                mask_draw = ImageDraw.Draw(mask)
                mask_draw.rectangle(xy, 1)
                fill = average_color(target, mask)
            case _:
                raise RuntimeError(f'Random shape {shape} is not handled by match statement')

        return f'{shape}:{xy}:{fill}'

    def random_shapes(self, target: Image.Image, n: int) -> list[str]:
        """Return a list of <n> new random shape strings using <target> as reference"""
        return [self.random_shape(target) for _ in range(n)]

    @staticmethod
    def draw_shape(img: Image.Image, shape_string: str) -> None:
        """Draw the shape described by unique <shape_string> on <img>
        """
        properties = shape_string.split(':')
        shape = properties[0]
        xy = eval(properties[1])
        fill = eval(properties[2])  # Fill color

        img_draw = ImageDraw.Draw(img)

        match shape:
            case 'ellipse':
                img_draw.ellipse(xy, fill)
            case 'rectangle':
                img_draw.rectangle(xy, fill)
            case _:
                raise ValueError(f"Shape string has invalid shape '{shape}'")
