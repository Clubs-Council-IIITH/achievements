import strawberry 
from typing import Union, Dict
from strawberry.fastapi import BaseContext
from functools import cached_property
from strawberry.types import Info as _Info
from strawberry.types.info import RootValueType
import json
from models import (
     Achievement, 
     InputCreateAchievementsBaseModel,
     InputEditAchievementsBaseModel,
     Achievement_Status)

class Context(BaseContext):
    """
    Class provides user metadata and cookies from request headers, has
    methods for doing this.
    """

    @cached_property
    def user(self) -> Union[Dict, None]:
        if not self.request:
            return None

        user = json.loads(self.request.headers.get("user", "{}"))
        return user

    @cached_property
    def cookies(self) -> Union[Dict, None]:
        if not self.request:
            return None

        cookies = json.loads(self.request.headers.get("cookies", "{}"))
        return cookies


Info = _Info[Context, RootValueType]
"""custom info Type for user metadata"""

@strawberry.experimental.pydantic.type(model= Achievement_Status, all_fields=True)
class AchievementStatusType:
    """
    Type for status details of an achievement
    """
    pass


@strawberry.experimental.pydantic.type(model=Achievement, all_fields=True)
class AchievementDetails:
    """
    Type for returning all the details of an achievement
    """
    pass

@strawberry.experimental.pydantic.input(model=InputCreateAchievementsBaseModel, all_fields=True)
class CreateAchievementDetails:
    """
    Type to act as input to the create achievement mutation
    """
    pass

@strawberry.experimental.pydantic.input(model = InputEditAchievementsBaseModel, all_fields=True)
class EditAchievementDetails:
    """
    Type to act as input to the edit achievement mutation
    """
    pass

