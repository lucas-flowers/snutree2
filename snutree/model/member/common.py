from pydantic import BaseModel


class BaseMember(BaseModel, arbitrary_types_allowed=True):
    pass
