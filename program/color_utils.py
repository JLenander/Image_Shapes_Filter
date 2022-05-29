"""Color Tools, including color difference map and average color"""

from PIL.Image import Image
from PIL import ImageChops


def color_difference_image(img1: Image, img2: Image) -> Image:
    """Return a new Image object created by taking the
    absolute value distance between <img1> and <img2>.

    <img1> and <img2> should be images convertible to RGB mode.

    Alpha channel is ignored in difference if included. Returned image is
    converted to RGB.

    Intended to be used for visual purposes, not optimized.
    """
    if img1.mode != 'RGB' or img2.mode != 'RGB':
        return ImageChops.difference(img1.convert('RGB'), img2.convert('RGB'))

    return ImageChops.difference(img1, img2)


def color_difference_score(img1: Image, img2: Image) -> int:
    """Return an integer representing how close <img1> is to <img2>.

    <img1> and <img2> should be the same dimensions and should be in RGB mode.

    The best and minimum score is 0, representing that all pixels are the same between
    the two images.

    The worst and maximum score can be found from color_difference.color_difference_max_score
    """
    histo = ImageChops.difference(img1, img2).histogram()
    return sum(histo[i] * (i % 256) for i in range(768))


def color_difference_max_score(img: Image) -> int:
    """Returns the maximum (worst) score for color difference between img and
    another image of the same dimensions.

    The maximum score is 255 difference * 3 color channels * x number of pixels
    """
    return 765 * img.width * img.height
