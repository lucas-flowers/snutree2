from enum import Enum
from typing import Literal, Union

from snutree.model.member.common import BaseMember
from snutree.model.member.sigmanu.affiliation import (
    Affiliation,
    AffiliationList,
    ChapterId,
)
from snutree.model.member.sigmanu.name import get_full_preferred_name
from snutree.model.semester import Semester


class Status(str, Enum):
    CANDIDATE = "Candidate"
    BROTHER = "Brother"
    ACTIVE = "Active"
    LEFT_SCHOOL = "Left School"
    ALUMNI = "Alumni"
    EXPELLED = "Expelled"

    def __str__(self) -> str:
        return self.value


class Expelled(BaseMember):
    status: Literal[Status.EXPELLED]

    chapter: ChapterId
    badge: int
    big_badge: int | None

    semester: Semester

    @property
    def name(self) -> str:
        return "Member Expelled"

    @property
    def affiliation(self) -> str:
        return str(self.badge)


class Knight(BaseMember):
    status: Literal[Status.ACTIVE, Status.LEFT_SCHOOL, Status.ALUMNI]

    chapter: ChapterId
    badge: int
    big_badge: int | None

    first_name: str
    preferred_name: str | None
    last_name: str

    semester: Semester
    affiliations: AffiliationList | None

    @property
    def name(self) -> str:
        return get_full_preferred_name(
            first_name=self.first_name,
            preferred_name=self.preferred_name,
            last_name=self.last_name,
        )

    @property
    def affiliation(self) -> str:
        affiliations = list(
            # Sort the list of affiliations, then remove duplicates while still
            # ensuring the primary affiliation is listed first.
            {
                affiliation: None
                for affiliation in [
                    Affiliation(self.chapter, self.badge),
                    *sorted(self.affiliations or []),
                ]
            }
        )
        return ", ".join(map(str, affiliations))


class Brother(BaseMember):
    status: Literal[Status.BROTHER]

    chapter: ChapterId
    big_badge: int | None

    last_name: str

    semester: Semester

    @property
    def name(self) -> str:
        return self.last_name

    @property
    def affiliation(self) -> str:
        return f"{self.chapter}\N{NO-BREAK SPACE}{self.status}"


class Candidate(BaseMember):
    status: Literal[Status.CANDIDATE]

    chapter: ChapterId
    big_badge: int | None

    first_name: str
    preferred_name: str | None
    last_name: str

    semester: Semester

    @property
    def name(self) -> str:
        return get_full_preferred_name(
            first_name=self.first_name,
            preferred_name=self.preferred_name,
            last_name=self.last_name,
        )

    @property
    def affiliation(self) -> str:
        return f"{self.chapter}\N{NO-BREAK SPACE}{self.status}"


SigmaNuMember = Union[
    Expelled,
    Knight,
    Brother,
    Candidate,
]
