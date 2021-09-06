from abc import ABC

from pydantic import BaseModel, validator

from snutree.model.tree import Member


class BaseMember(ABC, BaseModel, Member):
    @validator("*", pre=True)
    def empty_strings(cls, value: object) -> object:  # pylint: disable=no-self-argument
        if value == "":
            return None
        else:
            return value
