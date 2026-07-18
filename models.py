from pydantic import (
    BaseModel,
    Field, 
    field_validator,
    ValidationInfo,
    ConfigDict
)
from datetime import date, datetime
from typing import ( 
    List,
    Tuple
)
from mtypes import (
    PyObjectId,
    very_short_str_type,
    long_str_type,
    Achievement_Type,
    Achievement_Status_State
)

class Achievement_Status(BaseModel):
    """
    Type to keep information about Achievement_status
    """
    state: Achievement_Status_State = Achievement_Status_State.pending
    approved_by: str | None = None
    approved_datetime: datetime| None = None
    submission_datetime: datetime | None = None
    last_updated_datetime: datetime | None = None
    last_updated_by: str | None = None
    deletion_datetime : datetime | None = None
    deleted_by : str| None = None
    rejected_datetime: datetime| None = None
    rejected_by: str| None = None
    


class Achievement(BaseModel):
    """
    Model for an achievement
    attributes:
        id (mtypes.PyObjectId): id of the achievement
        name(str): name of the achievement
        clubids(List[str]):code of the club
        achievement_type(mtypes.Achievement_Type): Type of achievement
        userids(List[str]): Member Ids of all members involved in the achievement
        content(str): description and any associated content of the achievement
        blog_links(str): link to any website or blog post regarding achievement
        image_links(List[str]): image url links to all images to be shown
        dateperiod(Tuple[date, date]): The start and end dates of the achievement
    """
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name:very_short_str_type
    clubids:List[str]
    achievement_type:Achievement_Type
    userids: List[str]
    content:long_str_type
    blog_links :List[str] =[]
    image_links:List[str] = []
    dateperiod: Tuple[date, date]
    status: Achievement_Status= Field(default_factory=Achievement_Status)

    @field_validator("dateperiod")
    @classmethod
    def check_last_date(cls, value, info:ValidationInfo):
        if(value[1]<value[0]):
            raise ValueError("Last date cannot be earlier than first date")
        return value
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        # extra="forbid",
        str_strip_whitespace=True,
    )


class InputCreateAchievementsBaseModel(BaseModel):
    """
        Model for receiving input details of achievements
        Attributes:
                name(str): name of the achievement
                clubids(List[str]):code of the club
                achievement_type(mtypes.Achievement_Type): Type of achievement
                userids(List[str]): Member Ids of all members involved in the achievement
                content(str): description and any associated content of the achievement
                blog_links(str): link to any website or blog post regarding achievement
                image_links(List[str]): image url links to all images to be shown
                dateperiod(Tuple[date, date]): The start and end dates of the achievement
    """
    name:very_short_str_type
    clubids:List[str]
    achievement_type:Achievement_Type
    userids: List[str]
    content:long_str_type
    blog_links :List[str] =[]
    image_links:List[str] = []
    dateperiod: Tuple[date, date]


class InputEditAchievementsBaseModel(BaseModel):
    """
        Model for receiving input details of achievements
        Attributes:
                id (mtypes.PyObjectId): id of the achievement
                name(str): name of the achievement
                clubids(List[str]):code of the club
                achievement_type(mtypes.Achievement_Type): Type of achievement
                userids(List[str]): Member Ids of all members involved in the achievement
                content(str): description and any associated content of the achievement
                blog_links(str): link to any website or blog post regarding achievement
                image_links(List[str]): image url links to all images to be shown
                dateperiod(Tuple[date, date]): The start and end dates of the achievement
    """
    id: PyObjectId 
    name:very_short_str_type | None = None
    clubids:List[str] | None = None
    achievement_type:Achievement_Type | None = None
    userids: List[str] | None = None
    content:long_str_type | None = None
    blog_links :List[str] | None =None
    image_links:List[str]  | None = None
    dateperiod: Tuple[date, date] | None = None
    


