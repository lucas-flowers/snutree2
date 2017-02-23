import re

class Semester(int):

    matcher = re.compile('(Spring|Fall) (\d+)')

    def __new__(cls, *arg):

        if len(arg) == 1 and isinstance(arg[0], int):
            value = arg[0]

        elif len(arg) == 1 and isinstance(arg[0], str):

            arg = arg[0]
            match = Semester.matcher.match(arg)
            if match:
                season = 1 if match.group(1) == 'Fall' else 0
                year = int(match.group(2))
                value = 2 * year + season
            else:
                msg = 'semester names must match "{}"'
                vals = Semester.matcher.pattern, arg
                raise ValueError(msg.format(*vals))

        elif len(arg) == 2 and isinstance(arg[0], str) and isinstance(arg[1], int):

            season, year = arg
            season = {'Spring' : 0, 'Fall' : 1}.get(season)
            if not season:
                msg = 'semester seasons must match "Spring" or "Fall"'
                raise ValueError(msg)

            value = 2 * year + season

        else:
            raise TypeError('expected int, str, or *(str, int)')

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

