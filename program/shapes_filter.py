"""Evolution based image approximation filter

Terms used:
    round: each round comes up with the best shape(s) to apply to the image. New shapes are
        generated at the start of each round.
    iteration: each iteration within a round improves upon the best shape choices available.
        Shapes are generated each iteration based on the best shapes of the previous iteration.

Method:
    - Base canvas is average color of target image
    - For one round:
        - Randomly generate n shapes
        - Run n iterations:
            - For one iteration:
                - Calculate score for each shape applied to canvas based on how
                close the new image is to the target image
                - Select n top shapes
                - Make copies of shapes with small alterations to properties (evolution step)
                - If desired score or iterations reached, iterations end
        - Apply top shape(s) to image and complete round
"""

import logging
import random
from dataclasses import dataclass
from datetime import date
from typing import Type

from color_utils import (average_color_img, average_color_shape,
                         color_difference_score)
from color_utils import color_difference_score_normalized as similarity
from PIL import Image as Img
from PIL import ImageDraw, ImageShow
from PIL.Image import Image
from shapes.regular_polygon import RegularPolygon
from shapes.shape import Shape
from shapes.square import Square


@dataclass
class ShapeContainer:
    """The ShapeContainer is a class containing the shape, the position of the shape, and the color
    of the shape"""
    shape: Shape
    position: tuple[int]
    color: tuple[int]


class approximation_filter:
    """Class for parameter settings of the approximation filter.

    Attributes:
        list_shapes - The list of Shape classes that the filter will use
        num_shapes - the number of random shapes to generate for every round and the
            number of shapes that are evolved to each iteration.
        max_rounds - the maximum number of rounds (shapes) to generate for the image.
        similarity_threshold - the normalized difference score threshold at which the
            filter process is stopped. Either <max_rounds> or <similarity_threshold>
            can stop the filter process.
        num_iterations - the number of iterations per round. Every round is exactly this
            number of iterations.
        num_top_shapes - the number of shapes to keep per iteration.
    """
    list_shapes: list[Type[Shape]]
    num_shapes: int
    max_rounds: int
    similarity_threshold: float
    num_iterations: int
    num_top_shapes: int

    def __init__(self, list_shapes: list[Type[Shape]],
                 num_shapes: int = 200, max_rounds: int = 500,
                 similarity_threshold: float = 0.1, num_iterations: int = 10,
                 num_top_shapes: int = 20) -> None:
        """Creates the approximation filter using the supplied parameters.

        Parameter explanation in class description.

        Default parameter values (recommended value ranges):
            num_shapes - 200 (50, 500)
            max_rounds - 500 (25, 2000)
            similarity_threshold - 0.9 (0.6, 0.98)
            num_iterations - 10 (2, 30)
            num_top_shapes - 20 (10% of num_shapes)

        Requirements:
            - num_top_shapes <= num_shapes
            - 0.0 < similarity_threshold <= 1.0
        """
        self.list_shapes = list_shapes
        self.num_shapes = num_shapes
        self.max_rounds = max_rounds
        self.similarity_threshold = similarity_threshold
        self.num_iterations = num_iterations
        self.num_top_shapes = num_top_shapes

    def run_filter(self, target: Image, filename: str) -> None:
        """Basic filter function. Outputs file in output directory with name <filename>.

        <target> is an image object that the filter will attempt to approximate.
        <target> should be an image convertible to RGB mode.
        """
        raise NotImplemented

    def run_filter_with_viewer(self, target: Image, show_steps: int = 10) -> None:
        """Runs the filter function and calls the ipython viewer every <show_steps> shapes.
        Intended for use in a jupyter notebook.

        <target> is an image object that the filter will attempt to approximate.
        <target> should be an image convertible to RGB mode.
        """
        viewer = ImageShow.IPythonViewer()

        canvas = Img.new('RGB', target.size, average_color_img(target))
        canvas_draw = ImageDraw.Draw(canvas)

        shapes = []

        # Show blank canvas to start
        viewer.show(canvas)

        i = 0
        # Filter stops at self.similarity_threshold or at self.max_rounds
        while (i < self.max_rounds) and (similarity(target, canvas) >= self.similarity_threshold):
            shape_container = self._run_round(target, canvas)

            shapes.append(shape_container)
            shape_container.shape.draw_shape(canvas_draw,
                                             shape_container.shape,
                                             shape_container.position,
                                             shape_container.color)

            if i % show_steps == 0:
                viewer.show(canvas)

            logging.info(f"Round {i} finished with similarity score {similarity(target, canvas)}")

            i += 1

        if i == self.max_rounds:
            logging.info(f'Finished filter at max_rounds {i}')
        else:
            logging.info(f'Finished filter at similarity {similarity(target, canvas)}')

        viewer.show(canvas)

    def _run_round(self, target: Image, canvas: Image) -> ShapeContainer:
        """Return a single shape selected through <self.num_iterations> iterations.

        Each round starts with generating <self.num_shapes> shapes
        Before passing the shapes to the iteration method,
        the shapes are ranked using <self._rank_shapes>

        <target> is an image object representing the target image
        <canvas> is an image object representing the shapes drawn on the canvas through the filter
        """
        logging.debug("Running new round")
        # shape_selector = self._init_shape_selector(target, canvas)

        # Generate the list of shapes
        n_shapes = []
        for _ in range(self.num_shapes):
            # Select a random shape class to generate a random shape from
            # and generate a shape from that class
            new_shape = random.choice(self.list_shapes).generate_random_shape()
            # Generate a random position for this shape, making sure it is in the canvas
            new_pos = (random.randint(0, target.size[0]),
                       random.randint(0, target.size[1]))
            # Use the position to calculate the color of the shape
            new_color = average_color_shape(target, new_shape, new_pos)

            n_shapes.append(ShapeContainer(new_shape, new_pos, new_color))

        # Run the iterations for this round
        for i in range(self.num_iterations):
            ranked_n_shapes = self._rank_shapes(target, canvas, n_shapes)
            try:
                n_shapes = self._run_iteration(target, ranked_n_shapes)
            except Exception as e:
                logging.error(f'Failed to complete iteration on iteration {i}')
                logging.exception(e)

        # Shape at index 0 is the top shape.
        logging.debug(f"Best shape is {n_shapes[0]}")
        return n_shapes[0]

    def _run_iteration(self, target: Image, shapes: list[ShapeContainer]) -> list[ShapeContainer]:
        """Return a new list of <self.num_shapes> shapes that are evolved variants of
        <self.num_top_shapes> top ranked shapes from the list <shapes>.

        <shapes> must be ranked in accordance with self._rank_shapes

        The top shapes have their properties changed slightly
        """
        shapes_to_evolve = shapes[:self.num_top_shapes]
        new_shapes = []
        shape_num = 0
        while (shape_num < self.num_shapes):
            shape_to_evolve = shapes_to_evolve[shape_num % len(shapes_to_evolve)]
            evolved_shape = shape_to_evolve.shape.evolve_shape()

            # Evolve the two values for position
            evolved_position = shape_to_evolve.position
            for i in range(2):
                evolved_position[i] += random.randint(-10, 10)
                evolved_position[i] = min(0, max(target.size[i], evolved_position[i]))

            evolved_color = average_color_shape(target, evolved_shape, evolved_position)

            new_shapes.append(ShapeContainer(evolved_shape, evolved_position, evolved_color))

            shape_num += 1
        logging.debug(f'Evolved {shape_num} shapes from {len(shapes_to_evolve)} top shapes')
        return new_shapes

    def _rank_shapes(self, target: Image, canvas: Image, shapes: list[ShapeContainer]) -> list[ShapeContainer]:
        """Return a new list of shapes ranked by index (shape at index 0 has the best rank).
        Rank is score based on how the shape changes the <canvas>'s similarity to the <target>.

        The shape with the best change in similarity is ranked at index 0. (Note that this change
        may not necessarily be an improvement, ranking is relative to the other shapes in the list)
        """
        # List to be filled with (diff_score, shapecontainer) tuples
        shapes_with_score = []
        for shape_container in shapes:
            canvas_with_shape = canvas.copy()
            canvas_imgdraw = ImageDraw.Draw(canvas_with_shape)
            shape_container.shape.draw_shape(canvas_imgdraw,
                                             shape_container.shape,
                                             shape_container.position,
                                             shape_container.color)
            shapes_with_score.append((color_difference_score(canvas_with_shape, target), shape_container))

        # Sort by the similarity scores
        shapes_with_score.sort(key=lambda container: container[0])

        # Extract shape in sorted list
        return [shape for _, shape in shapes_with_score]


def main():
    """Main method"""
    logging.basicConfig(filename=f'../logs/filter_{date.today().strftime("%m_%d_%Y")}.log',
                        encoding='utf-8',
                        level=logging.DEBUG,
                        format='%(asctime)s [%(levelname)s] %(message)s',
                        datefmt='%m/%d/%Y %H:%M:%S')
    logging.info('Started main program')
    # Program Start
    try:
        filter = approximation_filter([RegularPolygon, Square])
        # Sample Target Image for testing
        target = Img.open('../example_imgs/squareColoredLarge.png').convert('RGB')
        filter.run_filter_with_viewer(target)
    except Exception as e:
        logging.exception(e)
        raise e
    # Program End
    logging.info('Program finished running')
    logging.shutdown()


if __name__ == '__main__':
    main()
