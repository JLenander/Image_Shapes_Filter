import random
from PIL import Image, ImageDraw
from program import shape_generator

import pytest
from hypothesis import assume, given
from hypothesis.strategies import integers, tuples


@pytest.fixture(scope='module')
def blank_target():
    return Image.new('RGB', (1000, 1000), (255, 255, 255))


def test_random_shape_tuple_fields(blank_target):
    bbox = [(-100, -100), (blank_target.width + 100, blank_target.height + 100)]
    selector = shape_generator.random_shape_selector(bbox, 1, 1000)
    random_PIL_shape = selector.get_shape_tuple()
    assert random_PIL_shape._fields == ('shape', 'xy', 'color')


def test_random_shape_tuple_format(blank_target):
    bbox = [(-100, -100), (blank_target.width + 100, blank_target.height + 100)]
    selector = shape_generator.random_shape_selector(bbox, 1, 1000)
    random_shape = selector.random_shape(blank_target)
    assert isinstance(random_shape.shape, str)
    assert isinstance(random_shape.xy, list)
    assert isinstance(random_shape.xy[0], tuple)
    assert isinstance(random_shape.xy[0][0], int)
    assert isinstance(random_shape.color, tuple)
    assert isinstance(random_shape.color[0], int)


@given(p1=tuples(integers(min_value=0, max_value=998), integers(min_value=0, max_value=998)))
def test_random_shape_in_bbox(p1, blank_target):
    # Construct p2 from p1 giving a minimum 2 pixel buffer (minimum 2x2 bounding box)
    p2 = (random.randint(p1[0] + 2, 1000), random.randint(p1[1] + 2, 1000))

    bbox = [p1, p2]
    selector = shape_generator.random_shape_selector(bbox, 1, 1000)
    shape_bbox = selector.random_shape(blank_target).xy
    assert bbox[0] <= shape_bbox[0] and shape_bbox[1] <= bbox[1]


@given(tuples(integers(min_value=0, max_value=999), integers(min_value=0, max_value=999)),
       tuples(integers(min_value=1, max_value=1000), integers(min_value=1, max_value=1000)))
def test_random_selector_draw(p1, p2):
    """Test drawing for random_shape_selector class given random bbox"""
    # Assume p1 is the topleft point and p2 is the bottomright point
    assume(p1[0] < p2[0])
    assume(p1[1] < p2[1])

    base_color = (255, 255, 255)
    draw_color = (0, 0, 0)
    random_PIL_shape = shape_generator.random_shape_selector.get_shape_tuple()
    expected = Image.new('RGB', (1000, 1000), base_color)
    expected_draw = ImageDraw.Draw(expected)
    expected_draw.rectangle([p1, p2], draw_color)
    shape = random_PIL_shape(shape='rectangle', xy=[p1, p2], color=draw_color)
    base = Image.new('RGB', (1000, 1000), base_color)
    shape_generator.random_shape_selector.draw_shape(base, shape)
    assert expected == base
