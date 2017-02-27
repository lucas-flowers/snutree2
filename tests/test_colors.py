from unittest import TestCase
from snutree.utilities.colors import ColorPicker

class TestColors(TestCase):

    def test_use_next(self):
        colors = ColorPicker([1, 2, 3, 4, 5])
        colors.use(3)
        self.assertSequenceEqual(colors._colors, [1, 2, 4, 5, 3])
        colors.use(3)
        self.assertSequenceEqual(colors._colors, [1, 2, 4, 5, 3])
        next(colors)
        next(colors)
        self.assertSequenceEqual(colors._colors, [4, 5, 3, 1, 2])

    def test_use_new(self):
        colors = ColorPicker([1, 2, 3, 4, 5])
        colors.use(6)
        self.assertSequenceEqual(colors._colors, [1, 2, 3, 4, 5])

    def test_use_all(self):
        colors = ColorPicker.from_graphviz()
        for _ in range(2 * len(colors)):
            next(colors)

