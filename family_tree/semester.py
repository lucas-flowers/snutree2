import re

class Semester(int):

    matcher = re.compile('(Spring|Fall) (\d+)')

    def __new__(cls, arg):

        if isinstance(arg, int):
            value = arg
        else:
            match = Semester.matcher.match(arg)
            if match:
                season = 1 if match.group(1) == 'Fall' else 0
                year = int(match.group(2))
                value = 2 * year + season
            else:
                raise ValueError(
                    'Semester names must match "{}" but "{}" was received'
                    .format(Semester.matcher.pattern, arg))

        return super(Semester, cls).__new__(cls, value)

    def __str__(self):
        year, season = divmod(self, 2)
        return '{} {}'.format('Fall' if season == 1 else 'Spring', year)

    def __add__(self, other):
        return Semester(super(Semester, self).__add__(other))

    __radd__ = __add__

