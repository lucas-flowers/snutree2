from enum import Enum
from typing import ClassVar, List, Literal, Optional, Union

from snutree.model.member.common import BaseMember
from snutree.model.member.sigmanu.affiliation import Affiliation
from snutree.model.member.sigmanu.name import get_full_preferred_name
from snutree.model.semester import Semester


class Status(str, Enum):
    CANDIDATE = "Candidate"
    BROTHER = "Brother"
    ACTIVE = "Active"
    LEFT_SCHOOL = "Left School"
    ALUMNI = "Alumni"
    EXPELLED = "Expelled"


class Expelled(BaseMember):

    status: Literal[Status.EXPELLED]

    chapter: str
    badge: str
    big_badge: Optional[str]

    semester: Semester

    @property
    def key(self) -> str:
        return str(self.badge)

    @property
    def name(self) -> str:
        return "Member Expelled"

    @property
    def affiliation(self) -> str:
        return str(self.badge)


class Knight(BaseMember):

    status: Literal[Status.ACTIVE, Status.LEFT_SCHOOL, Status.ALUMNI]

    chapter: str
    badge: str
    big_badge: Optional[str]

    first_name: str
    preferred_name: Optional[str]
    last_name: str

    semester: Semester
    affiliations: Optional[List[Affiliation]]

    @property
    def key(self) -> str:
        return str(self.badge)

    @property
    def name(self) -> str:
        return get_full_preferred_name(
            first_name=self.first_name,
            preferred_name=self.preferred_name,
            last_name=self.last_name,
        )

    @property
    def affiliation(self) -> str:
        return f"ΔΑ\N{NO-BREAK SPACE}{self.badge}"


class Brother(BaseMember):

    latest_brother_id: ClassVar[int] = 0

    status: Literal[Status.BROTHER]

    chapter: str
    big_badge: Optional[str]

    last_name: str

    semester: Semester

    @property
    def key(self) -> str:
        type(self).latest_brother_id += 1
        return f"brother{self.latest_brother_id}"

    @property
    def name(self) -> str:
        return self.last_name

    @property
    def affiliation(self) -> str:
        return f"ΔΑ\N{NO-BREAK SPACE}{self.status}"


class Candidate(BaseMember):

    latest_candidate_id: ClassVar[int] = 0

    status: Literal[Status.CANDIDATE]

    chapter: str
    big_badge: Optional[str]

    first_name: str
    preferred_name: Optional[str]
    last_name: str

    semester: Semester

    @property
    def key(self) -> str:
        type(self).latest_candidate_id += 1
        return f"candidate{self.latest_candidate_id}"

    @property
    def name(self) -> str:
        return get_full_preferred_name(
            first_name=self.first_name,
            preferred_name=self.preferred_name,
            last_name=self.last_name,
        )

    @property
    def affiliation(self) -> str:
        return f"ΔΑ\N{NO-BREAK SPACE}{self.status}"


SigmaNuMember = Union[
    Expelled,
    Knight,
    Brother,
    Candidate,
]
