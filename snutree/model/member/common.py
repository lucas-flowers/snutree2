from abc import ABC
from collections.abc import Callable
from typing import ParamSpec, TypeVar

import pydantic
from pydantic import BaseModel

P_1 = ParamSpec("P_1")
P_2 = ParamSpec("P_2")
R = TypeVar("R")


def identity(f: Callable[P_1, Callable[P_2, R]]) -> Callable[P_1, Callable[P_2, object]]:
    return f


# Remove some Any types that we don't care about
validator = identity(pydantic.validator)  # type: ignore[misc]


class BaseMember(ABC, BaseModel):
    @validator("*", pre=True)
    def empty_strings(cls, value: object) -> object:  # pylint: disable=no-self-argument
        if value == "":
            return None
        else:
            return value
