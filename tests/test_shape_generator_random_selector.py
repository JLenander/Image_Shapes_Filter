import random
from PIL import Image, ImageDraw
from program import shape_generator

import pytest
from hypothesis import assume, given
from hypothesis.strategies import integers, tuples


@pytest.fixture(scope='module')
def blank_target():
    return Image.new('RGB', (1000, 1000), (255, 255, 255))


@pytest.fixture(scope='module')
def random_selector():
    """Returns a random_shape_selector object with 1000x1000 bounding box,
    min_size of 10 and max_size of 100"""
    return shape_generator.random_shape_selector([(0, 0), (1000, 1000)], 10, 100)


def test_random_shape_str_format(random_selector, blank_target):
    shape_properties = random_selector.random_shape(blank_target).split(':')
    assert any(shape_properties[0] == shape for shape in ['ellipse', 'rectangle'])
    assert isinstance(eval(shape_properties[1]), list)
    assert isinstance(eval(shape_properties[2]), tuple)


def test_random_shape_point_format(random_selector, blank_target):
    """Ensure the xy coordinate point format is [(x0, y0), (x1, y1)]
    where (x0, y0) is the bottomleft point and (x1, y1) is the topright point"""
    shape_properties = random_selector.random_shape(blank_target).split(':')
    xy_coords = eval(shape_properties[1])
    assert isinstance(xy_coords, list)
    assert isinstance(xy_coords[0], tuple)
    assert isinstance(xy_coords[1], tuple)
    p1, p2 = xy_coords
    assert p1[0] < p2[0] and p1[1] < p2[1]


@given(p1=tuples(integers(min_value=0, max_value=998), integers(min_value=0, max_value=998)))
def test_random_shape_in_bbox(p1, blank_target):
    # Construct p2 from p1 giving a minimum 2 pixel buffer (minimum 4x4 bounding box)
    p2 = (random.randint(p1[0] + 2, 1000), random.randint(p1[1] + 2, 1000))

    bbox = [p1, p2]
    selector = shape_generator.random_shape_selector(bbox, 1, 1000)
    shape_bbox = eval(selector.random_shape(blank_target).split(':')[1])
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
    expected = Image.new('RGB', (1000, 1000), base_color)
    expected_draw = ImageDraw.Draw(expected)
    expected_draw.rectangle([p1, p2], draw_color)

    shape_str = f'rectangle:[{p1},{p2}]:{draw_color}'
    base = Image.new('RGB', (1000, 1000), base_color)
    shape_generator.random_shape_selector.draw_shape(base, shape_str)
    assert expected == base
