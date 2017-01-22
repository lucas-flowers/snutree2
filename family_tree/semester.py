import re

def semester_range(start, stop, step=1):
    i = start
    while i < stop:
        yield i
        i += step

class Semester(int):

    matcher = re.compile('(Spring|Fall) (\d+)')

    def __new__(cls, *arg):

        if len(arg) == 1:

            arg = arg[0]
            if isinstance(arg, int):
                value = arg

            elif isinstance(arg, str):

                match = Semester.matcher.match(arg)
                if match:
                    season = 1 if match.group(1) == 'Fall' else 0
                    year = int(match.group(2))
                    value = 2 * year + season
                else:
                    raise ValueError(
                            'Semester names must match "{}" but "{}" was received'
                            .format(Semester.matcher.pattern, arg)
                            )

        elif len(arg) == 2 and isinstance(arg[0], str) and isinstance(arg[1], int):

            season, year = arg

            if season == 'Spring':
                season = 0
            elif season == 'Fall':
                season = 1
            else:
                raise ValueError(
                        'Semester seasons must match "Spring" or "Fall", but "{}" was received'
                        .format(season)
                        )

            value = 2 * year + season

        else:
            raise TypeError(
                    'Expected int, str, or *(str, int) but received {}'
                    .format(type(arg))
                    )

        return super(Semester, cls).__new__(cls, value)

    def __repr__(self):
        year, season = divmod(self, 2)
        return '{} {}'.format('Fall' if season == 1 else 'Spring', year)

    def __str__(self):
        return repr(self)

    def __add__(self, other):
        return Semester(super(Semester, self).__add__(other))

    __radd__ = __add__

    def __sub__(self, other):
        return Semester(super(Semester, self).__sub__(other))

