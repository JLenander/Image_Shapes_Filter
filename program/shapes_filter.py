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
from datetime import date

from PIL import ImageShow
from PIL.Image import Image
from PIL import Image as Img

import shape_generator
from color_utils import color_difference_score, average_color
from color_utils import color_difference_score_normalized as similarity


class approximation_filter:
    """Class for parameter settings of the approximation filter.

    Attributes:
        shape_selector_class - the class of shape selector that is used.
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
    shape_selector_class: shape_generator.shape_selector
    num_shapes: int
    max_rounds: int
    similarity_threshold: float
    num_iterations: int
    num_top_shapes: int

    def __init__(self, shape_selector_class: shape_generator.shape_selector,
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
        self.shape_selector_class = shape_selector_class
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

        canvas = Img.new('RGB', target.size, average_color(target))

        shapes = []

        # Show blank canvas to start
        viewer.show(canvas)

        i = 0
        # Filter stops at self.similarity_threshold or at self.max_rounds
        while (i < self.max_rounds) and (similarity(target, canvas) >= self.similarity_threshold):
            shape = self._run_round(target, canvas)

            shapes.append(shape)
            self.shape_selector_class.draw_shape(canvas, shape)

            if i % show_steps == 0:
                viewer.show(canvas)

            logging.info(f"Round {i} finished with similarity score {similarity(target, canvas)}")

            i += 1

        if i == self.max_rounds:
            logging.info(f'Finished filter at max_rounds {i}')
        else:
            logging.info(f'Finished filter at similarity {similarity(target, canvas)}')

        viewer.show(canvas)

    def _init_shape_selector(self, target: Image, canvas: Image) -> shape_generator.shape_selector:
        """Returns a shape selector object initialized properly based on self.shape_selector_class

        Raises an error if no init implementation exists in method

        Implemented initializers:
            - shape_generator.random_shape_selector
        """
        rss = shape_generator.random_shape_selector
        if self.shape_selector_class == rss:
            logging.debug('Initialized random shape selector object')
            return rss([(-100, -100), (target.width + 100, target.height + 100)], 25,
                       min(1000, target.width, target.height))

        logging.error(f'Unimplemented init case for {self.shape_selector_class}')
        raise RuntimeError(f'Failed to initialize {self.shape_selector_class} object')

    def _run_round(self, target: Image, canvas: Image) -> tuple:
        """Return a single shape selected through <self.num_iterations> iterations.

        Each round starts with generating <self.num_shapes> shapes
        Before passing the shapes to the iteration method,
        the shapes are ranked using <self._rank_shapes>
        """
        logging.debug("Running new round")
        shape_selector = self._init_shape_selector(target, canvas)

        n_shapes = shape_selector.random_shapes(target, self.num_shapes)

        for i in range(self.num_iterations):
            ranked_n_shapes = self._rank_shapes(target, canvas, n_shapes)
            try:
                n_shapes = self._run_iteration(target, ranked_n_shapes, shape_selector)
            except Exception as e:
                logging.error(f'Failed to complete iteration on iteration {i}')
                logging.exception(e)

        # Shape at index 0 is the top shape.
        logging.debug(f"Best shape is {n_shapes[0]}")
        return n_shapes[0]

    def _run_iteration(self, target: Image, shapes: list[tuple],
                       shape_selector: shape_generator.shape_selector) -> list[tuple]:
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
            new_shapes.append(shape_selector.evolve_shape(target, shape_to_evolve))
            shape_num += 1
        logging.debug(f'Evolved {shape_num} shapes from {len(shapes_to_evolve)} top shapes')
        return new_shapes

    def _rank_shapes(self, target: Image, canvas: Image, shapes: list[tuple]) -> list[tuple]:
        """Return a new list of shapes ranked by index (shape at index 0 has the best rank).
        Rank is score based on how the shape changes the <canvas>'s similarity to the <target>.

        The shape with the best change in similarity is ranked at index 0. (Note that this change
        may not necessarily be an improvement, ranking is relative to the other shapes in the list)
        """
        # List to be filled with (diff_score, shape) tuples
        shapes_with_score = []
        for shape in shapes:
            canvas_with_shape = canvas.copy()
            self.shape_selector_class.draw_shape(canvas_with_shape, shape)
            shapes_with_score.append((color_difference_score(canvas_with_shape, target), shape))
        shapes_with_score.sort()

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
        filter = approximation_filter(shape_generator.random_shape_selector)
        # target = Img.open('../example_imgs/ProfilePic.png').convert('RGB')
        target = Img.open('../example_imgs/hat_no_transparency.png').convert('RGB')
        filter.run_filter_with_viewer(target)
    except Exception as e:
        logging.exception(e)
        raise e
    # Program End
    logging.info('Program finished running')
    logging.shutdown()


if __name__ == '__main__':
    main()
