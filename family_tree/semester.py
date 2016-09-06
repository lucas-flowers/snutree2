from functools import total_ordering
import re

@total_ordering
class Semester:

    matcher = re.compile('(Spring|Fall) (\d+)')

    def __init__(self, semester_string):

        match = Semester.matcher.match(semester_string)
        if match:
            self.season = match.group(1)
            self.year = int(match.group(2))
        elif semester_string == 'max':
            self.season = ''
            self.year = float('inf')
        elif semester_string == 'min':
            self.season = ''
            self.year = float('-inf')
        else:
            raise ValueError(
                'Semester objects must be constructed from strings of the form "{}", but constructor received "{}".'
                .format(Semester.matcher.pattern, semester_string))

    def __eq__(self, other):
        return (self.season, self.year) == (other.season, other.year)

    def __lt__(self, other):
        if self.year == other.year:
            return self.season == 'Spring' and other.season == 'Fall'
        else:
            return self.year < other.year

    def __str__(self):
        return '{} {}'.format(self.season, self.year)

    def increment(self):
        if self.season == 'Spring':
            return Semester('Fall {}'.format(self.year))
        elif self.season == 'Fall':
            return Semester('Spring {}'.format(self.year + 1))
        elif self.year == float('inf'):
            return Semester('max')
        else:
            return Semester('min')

    def decrement(self):
        if self.season == 'Fall':
            return Semester('Spring {}'.format(self.year))
        elif self.season == 'Spring':
            return Semester('Fall {}'.format(self.year - 1))
        elif self.year == float('inf'):
            return Semester('max')
        else:
            return Semester('min')



