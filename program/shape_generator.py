"""Objects for selection of shape to use in filter.

Each shape selector object handles random selection of shape(s) and random evolution
of shapes.
Each shape selector class also has a static method that handles drawing of shapes.

Shapes are denoted by a namedtuple defined by the class
"""

from PIL import ImageDraw, Image
from typing import Type
from collections import namedtuple
from color_utils import average_color
import random


class shape_selector():
    """Base Shape Selector class"""

    def __init__(self) -> None:
        raise NotImplementedError()

    def random_shape(self, target: Image.Image) -> tuple:
        """Return a new random shape represented by a string using <target> as reference"""
        raise NotImplementedError()

    def random_shapes(self, target: Image.Image, n: int) -> list[tuple]:
        """Return a list of <n> new random shape tuples using <target> as reference"""
        raise NotImplementedError()

    def evolve_shape(self, shape: tuple) -> str:
        """Return a new shape described by a tuple. The new shape is based on <shape> with
        slight variations in its properties.
        """
        raise NotImplementedError()

    @staticmethod
    def draw_shape(img: Image.Image, shape: tuple) -> None:
        """Draw the shape described by unique <shape> on <img>"""
        raise NotImplementedError()

    @staticmethod
    def shape_tuple_to_str(shape: tuple) -> str:
        """Return the string representation of the shape <shape>"""
        raise NotImplementedError()

    @staticmethod
    def shape_str_to_tuple(shape: str) -> tuple:
        """Return the namedtuple representation of the shape <shape>"""
        raise NotImplementedError()


class random_shape_selector(shape_selector):
    """Shape Selector randomly selecting from available shapes using the pillow/PIL draw library

    Shapes:
        - ellipse (including circle)
        - rectangle (including square)

    Randomized Properties of Shapes:
        - diameter/width/height/length
        - location
    """
    """ Instance Attributes """
    bbox: list[int]  # list of points in the form [x0, y0, x1, y1]
    min_size: int  # Minimum diameter/dimensions of shape in pixels
    max_size: int  # Maximum diameter/dimensions of shape in pixels

    """ Static Attributes """
    # namedtuple class for this selector's shape tuples
    shape_tuple = namedtuple('random_PIL_shape', ['shape', 'xy', 'color'])

    def __init__(self, bbox: list[tuple[int]] | list[int], min_size: int, max_size: int) -> None:
        """Initialize a new random_shape_selector object

        <bbox> is a list of two points in the form [(x0, y0), (x1, y1)] or the form [x0, y0, x1, y1]
        that define the bounding box for generated shapes. The coordinate system is such that (0, 0)
        is the top left corner of the image.
        The points should be such that x0 < x1 and y0 < y1 (topleft point first then bottomright)
        The bounding box may be within the image or external to the image. If it is bigger than the
        image, a portion of generated shapes will always be within the boundaries of the image.

        <min_size> is the minimum onscreen diameter/width/height/length of the shape in pixels
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

    def random_shape(self, target: Image.Image) -> tuple:
        """Return a new random shape represented by a namedtuple using <target> as reference.

        The shape is contained within the bounding box defined by self.bbox. A portion of
        the shape will always be within the <target> image boundaries.

        If an ellipse is generated such that no portion of the ellipse is within the image,
        the ellipse becomes a rectangle defined by the bounding box of the ellipse. This behavior
        is rare when self.bbox is reasonably set (within 150% of the image dimensions)

        The shape namedtuple is defined as random_shape_selector.shape_tuple
        """
        shapes = ['ellipse', 'rectangle']
        x0, y0, x1, y1 = self.bbox
        width, height = target.size

        # This first point is within the bounding box and the image dimensions
        p1x = random.randrange(max(0, x0) + self.min_size, min(x1, width) - self.min_size)
        p1y = random.randrange(max(0, y0) + self.min_size, min(y1, height) - self.min_size)

        # Randomly chooses the directions to go from the first point
        # Second point can be external to image dimensions but must be within bbox
        p2x = -1
        if random.random() > 0.5:
            # Second point is to the left of the first point
            p2x = random.randint(max(x0, p1x - self.max_size), p1x - self.min_size)
        else:
            # Second point is to the right of the first point
            p2x = random.randint(p1x + self.min_size, min(x1, p1x + self.max_size))

        p2y = -1
        if random.random() > 0.5:
            # Second point is below the first point
            p2y = random.randint(max(y0, p1y - self.max_size), p1y - self.min_size)
        else:
            p2y = random.randint(p1y + self.min_size, min(y1, p1y + self.max_size))

        # The first point in xy is the topleft point of the shape's bbox
        # The second point in xy is the bottomright point of the shape's bbox
        xy = [(min(p1x, p2x), min(p1y, p2y)), (max(p1x, p2x), max(p1y, p2y))]

        shape_name = random.choice(shapes)
        fill = self._get_average_color(target, shape_name, xy)
        if fill is False:  # Ellipse is not within image boundaries
            shape_name = 'rectangle'
            fill = self._get_average_color(target, shape_name, xy)

        return self.shape_tuple(shape=shape_name, xy=xy, color=fill)

    def random_shapes(self, target: Image.Image, n: int) -> list[tuple]:
        """Return a list of <n> new random shape tuples using <target> as reference
        The shape namedtuple is defined as random_shape_selector.shape_tuple
        """
        return [self.random_shape(target) for _ in range(n)]

    def evolve_shape(self, target: Image.Image, shape: tuple) -> tuple:
        """Return a new shape described by a namedtuple. The new shape is based on the random shape
        tuple <shape> with slight variations in its properties (new shape is guaranteed to be within
        the image boundaries)

        The evolved shape will have its color value recalculated to the average color of the shape
        mask in the target image.

        Property Variability:
            - X Position (up to +/- 5% of the image width in difference)
                Note: If the change in position hits the bounding box, this will squish the shape
            - Y Position (up to +/- 5% of the image height in difference)
                Note: If the change in position hits the bounding box, this will squish the shape
            - Scale      (up to +/- 20% scale)
                Note: scale is limited by self.max_size and self.min_size
                Note: shapes scale from their centerpoint (equally in each direction)
        """
        bx0, by0, bx1, by1 = self.bbox
        shape_name = shape.shape
        x0, y0 = shape.xy[0]
        x1, y1 = shape.xy[1]

        shape_width = x1 - x0
        shape_height = y1 - y0

        # Property variations
        x_variation_bound = int(target.width * 0.05)
        x_var = random.randint(-x_variation_bound, x_variation_bound)

        y_variation_bound = int(target.height * 0.05)
        y_var = random.randint(-y_variation_bound, y_variation_bound)

        # Scale divided by two so that shape scales from centerpoint
        scale_variation_bound = min(min((self.max_size - shape_width) / shape_width, 0.2),
                                    min((self.max_size - shape_height) / shape_height, 0.2))
        scale_var_percent = random.uniform(-scale_variation_bound, scale_variation_bound)
        scale_x_var = int((shape_width * scale_var_percent) / 2)
        scale_y_var = int((shape_height * scale_var_percent) / 2)

        # Inner max/min guarantees point stays within bounding box
        # Outer max/min guarantees point has a minimum of 1 px in the image boundaries
        #   ^ Achieves this by preventing topleft point from passing bottom or right side of image
        #   and by preventing bottomright point from passing top or left side of image.
        new_xy = [(min(max(bx0, x0 + x_var - scale_x_var), target.width - 1),
                   min(max(by0, y0 + y_var - scale_y_var), target.height - 1)),
                  (max(min(bx1, x1 + x_var + scale_x_var), 0),
                   max(min(by1, y1 + y_var + scale_y_var), 0))]

        new_color = self._get_average_color(target, shape_name, new_xy)
        if new_color is False:  # Ellipse is not within image boundaries
            shape_name = 'rectangle'
            new_color = self._get_average_color(target, shape_name, new_xy)

        return self.shape_tuple(shape=shape_name, xy=new_xy, color=new_color)

    def _get_average_color(self, target: Image.Image, shape_name: str, xy: list) -> tuple | bool:
        """Helper method to get the average color of the area defined by
        the shape's mask over the <target> image.

        If the method returns false, that means the ellipse does not have any pixels within the
        image boundaries. In this case, the ellipse should become a rectangle.
        """
        # Use mask to determine average color of the region in the target
        mask = Image.new('1', target.size)
        mask_draw = ImageDraw.Draw(mask)
        match shape_name:
            case 'ellipse':
                mask_draw.ellipse(xy, 1)

                # Ellipse drawn with bbox may not have shape within image.
                # In this case, return False and the ellipse should become a rectangle.
                if mask.getextrema() == (0, 0):
                    return False

                return average_color(target, mask)
            case 'rectangle':
                mask_draw.rectangle(xy, 1)
                return average_color(target, mask)
            case _:
                raise RuntimeError(f'Random shape {shape_name} is not handled by match statement')

    @staticmethod
    def draw_shape(img: Image.Image, shape: tuple) -> None:
        """Draw the shape described by the unique shape tuple <shape> on <img>
        """
        shape_name = shape.shape
        xy = shape.xy
        fill = shape.color

        img_draw = ImageDraw.Draw(img)

        match shape_name:
            case 'ellipse':
                img_draw.ellipse(xy, fill)
            case 'rectangle':
                img_draw.rectangle(xy, fill)
            case _:
                raise ValueError(f"Shape tuple has invalid shape '{shape_name}'")

    @staticmethod
    def get_shape_tuple() -> Type[tuple]:
        """Return this classes namedtuple instance used for describing shapes.

        Shape is defined by namedtuple with the following properties:
            shape - the name of the shape
            xy - the xy coordinates (coords defining shape for polygons or bbox for ellipse)
                 Note that the top left corner is (0, 0) in the pixel coordinate system
            color - RGB color (generated by average color of the same region in <target>)
        """
        return namedtuple('random_PIL_shape', ['shape', 'xy', 'color'])

    @staticmethod
    def shape_tuple_to_str(shape: tuple) -> str:
        """Return the string representation of the shape <shape>

        This shape string representation is shape, xy, and color delimited by ':'
        """
        return f'{shape.shape}:{shape.xy}:{shape.color}'

    @staticmethod
    def shape_str_to_tuple(shape: str) -> tuple:
        """Return the namedtuple representation of the shape <shape>"""
        shape_name, xy, color = shape.split(':')
        shape_tuple = random_shape_selector.get_shape_tuple()
        return shape_tuple(shape=shape_name, xy=eval(xy), color=eval(color))
