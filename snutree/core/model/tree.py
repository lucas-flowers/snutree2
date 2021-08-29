from dataclasses import dataclass
from typing import Generic, List, Optional, TypeVar, Union

from snutree.core.model.common import Rank

OptionalAnyRank = TypeVar("OptionalAnyRank", bound=Union[Rank, None])

T = TypeVar("T")


Cohort = object


@dataclass
class Tree(Generic[T]):
    """
    A tree.
    """

    @property
    def cohorts(self) -> Optional[List[Cohort]]:  # TODO A list of cohorts?
        ...

    @property
    def ranks(self) -> Optional[tuple[Rank, Rank]]:
        ...
