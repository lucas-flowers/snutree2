import re

class Semester(int):
    '''
    Represents a semester such as "Fall 1950" or "Spring 2015". Integer values
    can be added or subtracted from semesters, which increments/decrements them
    by one semester per unit.
    '''

    matcher = re.compile(r'(Spring|Fall) (\d+)')

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
                msg = 'semester names must match "{pattern}"'.format(pattern=Semester.matcher.pattern)
                raise ValueError(msg)

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
        year, is_fall = divmod(self, 2)
        season = 'Fall' if is_fall else 'Spring'
        return '{season} {year}'.format(season=season, year=year)

    def __str__(self):
        return repr(self)

    def __add__(self, other):
        return Semester(super(Semester, self).__add__(other))

    __radd__ = __add__

    def __sub__(self, other):
        return Semester(super(Semester, self).__sub__(other))

