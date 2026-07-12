from pydantic import (
    BaseModel,
    Field, 
    Tuple, 
    field_validator,
    ValidationInfo
)
from datetime import date
from typing import List
import strawberry
from mtypes import (
    PyObjectId,
    very_short_str_type,
    long_str_type,
    Achievement_Type
)

@strawberry.type
class Achievement(BaseModel):
    """
    Model for an achievement
    attributes:
        id (mtypes.PyObjectId): id of the achievement
        name(str): name of the achievement
        clubid(str):code of the club
        achievement_type(mtypes.Achievement_Type): Type of achievement
        memberids(List[str]): Member Ids of all members involved in the achievement
        content(str): description and any associated content of the achievement
        blog_link(str): link to any website or blog post regarding achievement
        image_links(List[str]): image url links to all images to be shown
        dateperiod(Tuple[date, date]): The start and end dates of the achievement
    """
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name:very_short_str_type
    clubid:str
    achievement_type:Achievement_Type
    memberids: List[str]
    content:long_str_type
    blog_links :List[str] =[]
    image_links:List[str] = []
    dateperiod: Tuple[date, date]

    @field_validator
    @classmethod
    def check_last_date(cls, value, info:ValidationInfo):
        if(value[1]<value[0]):
            raise ValueError("Last date cannot be earlier than first date")
        return value




