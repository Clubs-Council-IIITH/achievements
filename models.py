from datetime import date, datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationInfo,
    field_validator,
)

from mtypes import (
    Achievement_Status_State,
    Achievement_Type,
    PyObjectId,
    long_str_type,
    short_str_type,
    very_short_str_type,
)


class Achievement_Status(BaseModel):
    """
    Type to keep information about Achievement_status
    """

    state: Achievement_Status_State = Achievement_Status_State.pending
    approved_by: str | None = None
    approved_datetime: datetime | None = None
    submission_datetime: datetime | None = None
    last_updated_datetime: datetime | None = None
    last_updated_by: str | None = None
    deletion_datetime: datetime | None = None
    deleted_by: str | None = None
    rejected_datetime: datetime | None = None
    rejected_by: str | None = None


class Achievement(BaseModel):
    """
    Model for an achievement
    attributes:
        id (mtypes.PyObjectId): id of the achievement
        name(str): name of the achievement
        code(str): An unique Achievement code
        clubids(List[str]):code of the club
        achievement_type(mtypes.Achievement_Type): Type of achievement
        userids(List[str]): Member Ids of all members involved in the
            achievement
        content(str): description and any associated content of the achievement
        blog_links(str): link to any website or blog post regarding achievement
        image_links(List[str]): image url links to all images to be shown
        dateperiod(Tuple[date, date]): The start and end dates of the
            achievement
    """

    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: very_short_str_type
    code: str | None = None
    clubids: list[str]
    achievement_type: Achievement_Type
    userids: list[str]
    content: long_str_type
    blog_links: list[str] = []
    image_links: list[str] = []
    dateperiod: tuple[date, date]
    status: Achievement_Status = Field(default_factory=Achievement_Status)
    venue: short_str_type | None = None

    @field_validator("dateperiod")
    @classmethod
    def check_last_date(cls, value, info: ValidationInfo):
        if value[1] < value[0]:
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
        userids(List[str]): Member Ids of all members involved in the
            achievement
        content(str): description and any associated content of the
            achievement
        blog_links(str): link to any website or blog post regarding
            achievement
        image_links(List[str]): image url links to all images to be shown
        dateperiod(Tuple[date, date]): The start and end dates of the
            achievement
    """

    name: very_short_str_type
    clubids: list[str]
    achievement_type: Achievement_Type
    userids: list[str]
    content: long_str_type
    blog_links: list[str] = []
    image_links: list[str] = []
    dateperiod: tuple[date, date]
    venue: short_str_type | None = None


class InputEditAchievementsBaseModel(BaseModel):
    """
    Model for receiving input details of achievements
    Attributes:
        id (mtypes.PyObjectId): id of the achievement
        code(str): An Unique achievement code for the achievement
        name(str): name of the achievement
        clubids(List[str]):code of the club
        achievement_type(mtypes.Achievement_Type): Type of achievement
        userids(List[str]): Member Ids of all members involved in the
            achievement
        content(str): description and any associated content of the
            achievement
        blog_links(str): link to any website or blog post regarding
            achievement
        image_links(List[str]): image url links to all images to be shown
        dateperiod(Tuple[date, date]): The start and end dates of the
            achievement
    """

    id: PyObjectId
    name: very_short_str_type | None = None
    clubids: list[str] | None = None
    achievement_type: Achievement_Type | None = None
    userids: list[str] | None = None
    content: long_str_type | None = None
    blog_links: list[str] | None = None
    image_links: list[str] | None = None
    dateperiod: tuple[date, date] | None = None
    venue: short_str_type | None = None

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        # extra="forbid",
        str_strip_whitespace=True,
    )
