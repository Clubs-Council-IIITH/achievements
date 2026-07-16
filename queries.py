"""
Queries for achievements
"""

from typing import List
from bson import ObjectId

import strawberry

from db import achievementsdb
from models import Achievement

from otypes import Achievement_Details, Info

from utils import get_club, get_user    


@strawberry.field
async def allAchievements(info: Info) -> List[Achievement_Details]:
    """
    Fetches all the achievements

    Returns
    (List[otypes.Achievement_Details]): A list of all Achievements
    """
    achievements = await achievementsdb.find().to_list(length=None)

    return [
        Achievement_Details.from_pydantic(Achievement.model_validate(achievement))
        for achievement in achievements
    ]


@strawberry.field
async def achievementById(achievementid: str) -> Achievement_Details:
    """
    Fetches an achievement with the given id

    Args:
        achievementid (str): The id of the achievement to be fetched.
        info (otypes.Info): The context information of user for the request
    
    Returns:
        (otypes.Achievement_Details): Detaile regarding the achievement with the given id

    Raises:
        Exception: Achievement with given code does not exist.

    """
    achievement = await achievementsdb.find_one({"_id": ObjectId(achievementid)})

    if (achievement is None):
        raise Exception("Achievement with given id does not exist")
    
    return Achievement_Details.from_pydantic(Achievement.model_validate(achievement))


@strawberry.field
async def achievementsByClub(cid: str, info:Info) -> List[Achievement_Details]:
    """
    Fetches list of achievements with the give clubid

    Arg:
    clubid (str) : The id of the club whose achievements are to be fetched.
    info (otypes.Info): The context information of user for the request.

    Returns:
    (List[otypes.Achievement_Details]): A list of Achievements which matches the cubid

    """
    club = await get_club(cid, info.context.cookies)

    if club is None:
        raise Exception("Club with given id does not exist")
    
    achievements = await achievementsdb.find(
        {
        "clubids": cid,
        }
    ).to_list(None)

    return [
        Achievement_Details.from_pydantic(Achievement.model_validate(achievement))
        for achievement in achievements
    ]
    

@strawberry.field
async def achievementsByUser(uid: str, info:Info) -> List[Achievement_Details]:
    """
    Fetches list of achievements with the given userid

    Arg:
    uid (str) : The id of the user whose achievements are to be fetched.
    info (otypes.Info): The context information of user for the request.

    Returns: 
    (List[otypes.Achievement_Details]): A list of Achievements which matches the userid

    """

    # user = await get_user(uid, info.context.cookies)

    # if user is None:
    #     raise Exception("User with given id does not exist")
    
    achievements = await achievementsdb.find(
        {
        "userids": uid,
        }
    ).to_list(None)

    return [
        Achievement_Details.from_pydantic(Achievement.model_validate(achievement))
        for achievement in achievements
    ]


#register all the queries
queries = [
    allAchievements,
    achievementById,
    achievementsByUser,
    achievementsByClub,
]