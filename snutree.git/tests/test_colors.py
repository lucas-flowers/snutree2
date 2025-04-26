from snutree.utilities.colors import ColorPicker

def test_use_next():
    # pylint: disable=protected-access
    colors = ColorPicker([1, 2, 3, 4, 5])
    colors.use(3)
    assert list(colors._colors) == [1, 2, 4, 5, 3]
    colors.use(3)
    assert list(colors._colors) == [1, 2, 4, 5, 3]
    next(colors)
    next(colors)
    assert list(colors._colors) == [4, 5, 3, 1, 2]

def test_use_new():
    # pylint: disable=protected-access
    colors = ColorPicker([1, 2, 3, 4, 5])
    colors.use(6)
    assert list(colors._colors) == [1, 2, 3, 4, 5]

def test_use_all():
    colors = ColorPicker.from_graphviz()
    for _ in range(2 * len(colors)):
        next(colors)

