from pydantic import BaseModel
import strawberry
from mtypes import (
    PyObjectId,
    very_short_str_type
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