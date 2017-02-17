from ..entity import Initiate
from ..utilities import nonempty_string, optional_nonempty_string, optional_semester_like

class KeylessInitiate(Initiate):

    schema = {
            'status' : {'allowed' : ['KeylessInitiate']},
            'name' : nonempty_string,
            'big_name' : optional_nonempty_string,
            'pledge_semester' : optional_semester_like,
            }

    def __init__(self,
            status=None,
            name=None,
            pledge_semester=None,
            big_name=None
            ):

        self.key = name
        self.semester = pledge_semester
        self.parent = big_name

    def get_key(self):
        return self.key

    def get_dot_label(self):
        return self.key

