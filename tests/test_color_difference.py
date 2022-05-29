from program import color_difference
from PIL import Image


def test_difference_score_same():
    img1 = Image.new('RGB', (100, 100), (255, 0, 0))
    img2 = Image.new('RGB', (100, 100), (255, 0, 0))
    assert color_difference.color_difference_score(img1, img2) == 0


def test_difference_score():
    img1 = Image.new('RGB', (100, 100), (255, 0, 0))
    img2 = Image.new('RGB', (100, 100), (250, 0, 0))
    expected_difference = 5 * 100 * 100  # difference of 5 in red channel per pixel
    assert color_difference.color_difference_score(img1, img2) == expected_difference


def test_difference_max_score():
    img = Image.new('RGB', (25, 4), (0, 0, 0))
    expected_max = (25 * 4) * (255 * 3)  # 100 pixels, max diff for each of 3 channels is 0 -> 255
    assert color_difference.color_difference_max_score(img) == expected_max
