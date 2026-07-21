from bson import ObjectId
from enum import StrEnum, auto
from pydantic_core import core_schema
from pydantic import (
    StringConstraints,    
)
from typing import (
    Annotated, 
    Any,
    
)
import strawberry


very_short_str_type = Annotated[
    str, StringConstraints(min_length=1, max_length=200)
]
"""very short string type with min length 1 and max length 200"""
short_str_type = Annotated[
    str,
    StringConstraints(max_length=1000),
]
"""short string type with max length 1000"""
medium_str_type = Annotated[
    str,
    StringConstraints(max_length=5000),
]
"""medium string type with max length 5000"""
long_str_type = Annotated[
    str,
    StringConstraints(max_length=10000),
]
""" long string type with max length 10000"""

class PyObjectId(ObjectId):
    """
    Class for handling MongoDB document ObjectIds for 'id' fields in Models.
    """

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler):
        return core_schema.union_schema(
            [
                # check if it's an instance first before doing any further work
                core_schema.is_instance_schema(ObjectId),
                core_schema.no_info_plain_validator_function(cls.validate),
            ],
            serialization=core_schema.to_string_ser_schema(),
        )

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")

@strawberry.enum
class Achievement_Type(StrEnum):
    """
    Enum to denote the type of achievement
    """
    project = auto()
    competition = auto()
    other = auto()

@strawberry.enum
class Achievement_Status_State(StrEnum):
    """
    Enum to denote the state of the achievement
    """
    approved = auto()
    pending = auto()
    deleted = auto()
    rejected = auto()



