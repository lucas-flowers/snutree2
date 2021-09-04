from enum import Enum
from typing import List, Literal, Optional

from pydantic import BaseModel

from snutree.model.member.sigmanu.affiliation import Affiliation
from snutree.model.semester import Semester


class Status(str, Enum):
    CANDIDATE = "Candidate"
    BROTHER = "Brother"
    ACTIVE = "Active"
    LEFT_SCHOOL = "Left School"
    ALUMNI = "Alumni"
    EXPELLED = "Expelled"


class Expelled(BaseModel):

    status: Literal[Status.EXPELLED]

    badge: int
    big_badge: Optional[int]

    semester: Semester


class Knight(BaseModel):

    status: Literal[Status.ACTIVE, Status.LEFT_SCHOOL, Status.ALUMNI]

    badge: int
    big_badge: Optional[int]

    first_name: str
    preferred_name: Optional[str]
    last_name: str

    semester: Semester
    affiliations: List[Affiliation]


class Brother(BaseModel):

    status: Literal[Status.BROTHER]

    big_badge: Optional[int]

    last_name: str

    semester: Semester


class Candidate(BaseModel):

    status: Literal[Status.CANDIDATE]

    big_badge: Optional[int]

    first_name: str
    preferred_name: Optional[str]
    last_name: str

    semester: Semester
