"""
Types and Inputs for achievements subgraph
"""

import json
from functools import cached_property

import strawberry
from strawberry.fastapi import BaseContext
from strawberry.types import Info as _Info
from strawberry.types.info import RootValueType

from models import (
    Achievement,
    Achievement_Status,
    InputCreateAchievementsBaseModel,
    InputEditAchievementsBaseModel,
)


class Context(BaseContext):
    """
    Class provides user metadata and cookies from request headers, has
    methods for doing this.
    """

    @cached_property
    def user(self) -> dict | None:
        if not self.request:
            return None

        user = json.loads(self.request.headers.get("user", "{}"))
        return user

    @cached_property
    def cookies(self) -> dict | None:
        if not self.request:
            return None

        cookies = json.loads(self.request.headers.get("cookies", "{}"))
        return cookies


Info = _Info[Context, RootValueType]
"""custom info Type for user metadata"""


@strawberry.experimental.pydantic.type(
    model=Achievement_Status, all_fields=True
)
class AchievementStatusType:
    """
    Type for status details of an achievement
    """


@strawberry.experimental.pydantic.type(model=Achievement, all_fields=True)
class AchievementDetails:
    """
    Type for returning all the details of an achievement
    """


@strawberry.experimental.pydantic.input(
    model=InputCreateAchievementsBaseModel, all_fields=True
)
class CreateAchievementDetails:
    """
    Type to act as input to the create achievement mutation
    """


@strawberry.experimental.pydantic.input(
    model=InputEditAchievementsBaseModel, all_fields=True
)
class EditAchievementDetails:
    """
    Type to act as input to the edit achievement mutation
    """
