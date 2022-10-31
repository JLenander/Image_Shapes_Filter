from PIL import Image
from program import color_utils, shapes_filter, shape_generator

import pytest


@pytest.fixture(scope='module')
def white_image():
    """Blank white 1000x1000 px image"""
    return Image.new('RGB', (1000, 1000), (255, 255, 255))


@pytest.fixture(scope='module')
def red_image():
    """Blank red 1000x1000 px image"""
    return Image.new('RGB', (1000, 1000), (255, 0, 0))


@pytest.fixture(scope='module')
def random_shape_approx_filter():
    """Approximation filter with random_shape_selector class and default settings"""
    return shapes_filter.approximation_filter(shape_generator.random_shape_selector)


@pytest.fixture(scope='module')
def rss():
    """Random Shape Selector objectwith 1000x1000 px bbox and min_size 10, max_size 100"""
    return shape_generator.random_shape_selector([(0, 0), (1000, 1000)], 10, 100)


"""Tests for random shape selector (rss) class"""


def test_rss_rank_shapes_known_rank(white_image, random_shape_approx_filter):
    random_PIL_shape = shape_generator.random_shape_selector.shape_tuple
    shapes = [random_PIL_shape('rectangle', [(0, 0), (1000, 1000)], (255, 255, 255)),
              random_PIL_shape('rectangle', [(0, 0), (1000, 1000)], (127, 127, 127)),
              random_PIL_shape('rectangle', [(0, 0), (1000, 1000)], (255, 0, 0)),
              random_PIL_shape('rectangle', [(0, 0), (1000, 1000)], (0, 0, 0))]
    ranked_shapes = random_shape_approx_filter._rank_shapes(white_image, white_image, shapes)
    assert shapes == ranked_shapes


# Run the test 20 times to ensure reasonable probablility of correctness
@pytest.mark.parametrize('exec_number', range(20))
def test_rss_rank_shapes(white_image, red_image, random_shape_approx_filter, rss, exec_number):
    random_PIL_shape = shape_generator.random_shape_selector.shape_tuple
    shapes = [random_PIL_shape('rectangle', [(0, 0), (1000, 1000)], (255, 255, 255)),
              random_PIL_shape('rectangle', [(0, 0), (1000, 1000)], (127, 127, 127)),
              random_PIL_shape('rectangle', [(0, 0), (1000, 1000)], (0, 0, 0))]

    # Scores of the 3 static shapes (in order)
    scores = []
    for shape in shapes:
        canvas_with_shape = white_image.copy()
        shape_generator.random_shape_selector.draw_shape(canvas_with_shape, shape)
        scores.append(color_utils.color_difference_score(canvas_with_shape, white_image))

    # generate random shape, calculate its score, and identify the index it needs to be in.
    random_shape = rss.random_shape(red_image)
    canvas_with_shape = white_image.copy()
    shape_generator.random_shape_selector.draw_shape(canvas_with_shape, random_shape)
    random_shape_score = color_utils.color_difference_score(canvas_with_shape, white_image)
    index = 0
    while (index < 3) and (random_shape_score > scores[index]):
        index += 1

    # random_shape could be placed in two different indices because the scores matched.
    if random_shape_score in scores:
        # Shape before other shape with same score
        expected_shape_before = shapes.copy()
        expected_shape_before.insert(index, random_shape)
        # Shape after other shape with same score
        expected_shape_after = shapes.copy()
        expected_shape_after.insert(index + 1, random_shape)

        input = shapes.copy()
        input.append(random_shape)

        ranked_shapes = random_shape_approx_filter._rank_shapes(white_image, white_image, input)
        assert (expected_shape_before == ranked_shapes) or (expected_shape_after == ranked_shapes)
    else:
        expected_list = shapes.copy()
        expected_list.insert(index, random_shape)
        input = shapes.copy()
        input.append(random_shape)

        ranked_shapes = random_shape_approx_filter._rank_shapes(white_image, white_image, input)
        assert expected_list == ranked_shapes
