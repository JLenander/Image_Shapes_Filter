from program import color_utils
from PIL import Image, ImageDraw

from hypothesis import given
from hypothesis.strategies import integers, tuples


def test_difference_score_same():
    img1 = Image.new('RGB', (100, 100), (255, 0, 0))
    img2 = Image.new('RGB', (100, 100), (255, 0, 0))
    assert color_utils.color_difference_score(img1, img2) == 0


def test_difference_score():
    img1 = Image.new('RGB', (100, 100), (255, 0, 0))
    img2 = Image.new('RGB', (100, 100), (250, 0, 0))
    expected_difference = 5 * 100 * 100  # difference of 5 in red channel per pixel
    assert color_utils.color_difference_score(img1, img2) == expected_difference


def test_difference_max_score():
    img = Image.new('RGB', (25, 4), (0, 0, 0))
    expected_max = (25 * 4) * (255 * 3)  # 100 pixels, max diff for each of 3 channels is 0 -> 255
    assert color_utils.color_difference_max_score(img) == expected_max


@given(tuples(integers(min_value=0, max_value=255),
              integers(min_value=0, max_value=255),
              integers(min_value=0, max_value=255)))
def test_average_color_solid_canvas(expected_color):
    img = Image.new('RGB', (1000, 500), expected_color)
    assert color_utils.average_color(img) == expected_color


@given(integers(min_value=0, max_value=255),
       integers(min_value=0, max_value=255),
       integers(min_value=0, max_value=255))
def test_average_color_no_mask(r, g, b):
    img = Image.new('RGB', (1000, 500), (r, g, b))
    img_draw = ImageDraw.Draw(img)
    img_draw.polygon([(0, 0), (499, 0), (499, 499), (0, 499)], fill=(0, 0, 0))
    # Image is half black, half (r,g,b)
    expected_color = (r // 2, g // 2, b // 2)
    assert color_utils.average_color(img) == expected_color


@given(tuples(integers(min_value=0, max_value=255),
              integers(min_value=0, max_value=255),
              integers(min_value=0, max_value=255)))
def test_average_color_mask(expected_color):
    img = Image.new('RGB', (1000, 500), expected_color)
    img_draw = ImageDraw.Draw(img)
    img_draw.polygon([(0, 0), (499, 0), (499, 499), (0, 499)], fill=(0, 0, 0))

    # Draw mask over half of image with expected_color
    mask = Image.new('1', (1000, 500), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.polygon([(500, 0), (1000, 0), (1000, 500), (500, 500)], 1)
    assert color_utils.average_color(img, mask) == expected_color
