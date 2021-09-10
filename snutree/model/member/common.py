from abc import ABC

from pydantic import BaseModel, validator


class BaseMember(ABC, BaseModel):
    @validator("*", pre=True)
    def empty_strings(cls, value: object) -> object:  # pylint: disable=no-self-argument
        if value == "":
            return None
        else:
            return value
