"""Color Tools, including color difference map and average color"""

import logging
from typing import Optional

from PIL import ImageChops, ImageStat
from PIL.Image import Image


def color_difference_image(img1: Image, img2: Image) -> Image:
    """Return a new Image object created by taking the
    absolute value distance between <img1> and <img2>.

    <img1> and <img2> should be images convertible to RGB mode.

    Alpha channel is ignored in difference if included. Returned image is
    converted to RGB.

    Intended to be used for visual purposes, not optimized.
    """
    if img1.mode != 'RGB' or img2.mode != 'RGB':
        logging.info(f'Images {id(img1)=} or {id(img2)=} are not in RGB mode,'
                     'converting them to RGB for color_difference_image method.')
        return ImageChops.difference(img1.convert('RGB'), img2.convert('RGB'))

    return ImageChops.difference(img1, img2)


def color_difference_score(img1: Image, img2: Image) -> int:
    """Return an integer representing how close <img1> is to <img2>.

    <img1> and <img2> should be the same dimensions and should be in RGB mode.

    The best and minimum score is 0, representing that all pixels are the same between
    the two images.

    The worst and maximum score can be found from color_utils.color_difference_max_score
    """
    histo = ImageChops.difference(img1, img2).histogram()
    return sum(histo[i] * (i % 256) for i in range(768))


def color_difference_max_score(img: Image) -> int:
    """Returns the maximum (worst) score for color difference between img and
    another image of the same dimensions.

    The maximum score is 255 difference * 3 color channels * x number of pixels
    """
    return 765 * img.width * img.height


def color_difference_score_normalized(img1: Image, img2: Image) -> float:
    """Return a float representing how close <img1> is to <img2>.

    <img1> and <img2> should be the same dimensions and should be in RGB mode.

    The best and minimum score is 0.0, representing that all of the pixels
    between the two images are the same.

    The worst and maximum score is 1.0, representing the maximum difference
    between the two images

    This score is a version of color_utils.color_difference_score normalized to
    the range [0,1].
    """
    return color_difference_score(img1, img2) / color_difference_max_score(img1)


def average_color(img: Image, mask: Optional[Image] = None) -> tuple[int]:
    """Return the average color of <img> within the optional <mask> or for the entire image.

    Average color is returned as an rgb tuple of integers.

    <img> should be in RGB mode
    <mask> should be a valid pillow mask (namely same dimensions as <img> and in mode 1 or L)
    """
    return _average_color_image_stats(img, mask)


def _average_color_image_stats(img: Image, mask: Optional[Image]) -> tuple[int]:
    """Return the average color of <img> within the optional <mask> or for the entire image.

    Pillow ImageStat implementation of average color.
    <img> should be in RGB mode
    <mask> should be a valid pillow mask (namely same dimensions as <img> and in mode 1 or L)
    """
    try:
        r, g, b = ImageStat.Stat(img, mask).mean
        return (int(r), int(g), int(b))
    except ZeroDivisionError:
        logging.error(f'Image mask covers whole image for img {id(img)=}'
                      f' so no average color can be calculated {mask=}')
        raise ValueError('The mask covers the whole image so no average color can be calculated')
