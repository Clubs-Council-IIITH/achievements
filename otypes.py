"""
Types and Inputs for achievements subgraph
"""

import json
from functools import cached_property
from typing import Dict, Union

import strawberry 
from strawberry.fastapi import BaseContext
from strawberry.types import Info as _Info
from strawberry.types.info import RootValueType

from models import Achievement

# custom context class
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

@strawberry.experimental.pydantic.type(model=Achievement, all_fields=True)
class Achievement_Details:
    """
    Type for returning all the details of an achievement
    """
    pass