"""
Queries for achievements
"""

from typing import List
from bson import ObjectId

import strawberry
from db import achievementsdb
from models import Achievement
from otypes import AchievementDetails, Info
from mtypes import Achievement_Status_State
from utils import get_club, get_user, get_clubs


@strawberry.field
async def allAchievements(info: Info) -> List[AchievementDetails]:
    """
    Fetches all the achievements

    Args:
        info (otypes.Info): User metadata and cookies.

    Returns
        (List[otypes.AchievementDetails]): A list of all Achievements
    """
    user = info.context.user
    achievements = []

    if (user is not None and user["role"] in ["cc", "slo"]):
        achievements = await achievementsdb.find().to_list(length=None)
    else:
        achievements =await achievementsdb.find({"status.state": "approved"}).to_list(
            length=None
        )

    return [
        AchievementDetails.from_pydantic(Achievement.model_validate(achievement))
        for achievement in achievements
    ]


@strawberry.field
async def achievementById(achievementid: str, info: Info) -> AchievementDetails:
    """
    Fetches an achievement with the given id

    Args:
        achievementid (str): The id of the achievement to be fetched.
        info (otypes.Info): The context information of user for the request
    
    Returns:
        (otypes.AchievementDetails): Detaile regarding the achievement with the given id

    Raises:
        Exception: Cannot access the achievement. Either you do not have permission to access it or it does not exist.

    """
    user = info.context.user
    achievement = await achievementsdb.find_one({"_id": achievementid})

    allclubs = await get_clubs(info.context.cookies)
    list_allclubs = list()
    for club in allclubs:
        list_allclubs.append(club["cid"])

    if (
        achievement is None
        or (
            achievement["status"]["state"]
            not in {Achievement_Status_State.approved.value}
            and (
                user is None
                or (
                    user["role"] not in {"cc", "slc", "slo"}
                    and (
                        user["role"] != "club"
                        or (
                            user["uid"] not in achievement["clubids"]
                        )
                    )
                )
            )
        )
    ):
        raise Exception(
            "Can not access achievement. Either it does not exist or user does not have perms."  
        )
    
    return AchievementDetails.from_pydantic(Achievement.model_validate(achievement))


@strawberry.field
async def achievementsByClub(cid: str, info:Info) -> List[AchievementDetails]:
    """
    Fetches list of achievements with the give clubid

    Arg:
    cid (str) : The id of the club whose achievements are to be fetched.
    info (otypes.Info): The context information of user for the request.

    Returns:
    (List[otypes.AchievementDetails]): A list of Achievements which matches the cubid

    """
    user = info.context.user
    club = await get_club(cid, info.context.cookies)

    if club is None:
        raise Exception("Club with given id does not exist")
    
    can_access = (
        user is not None
        and (
            user["role"] in ["cc", "slo"]
            or (
                user["role"] == "club"
                and user["uid"] == club["cid"]  
            )
        )
    )

    if can_access:
        achievements = await achievementsdb.find(
            {
            "clubids": cid,
            }
        ).to_list(None)
    else:
        achievements = await achievementsdb.find(
            {"clubids": cid, "status.state": "approved"}
        ).to_list(None)

    return [
        AchievementDetails.from_pydantic(Achievement.model_validate(achievement))
        for achievement in achievements
    ]
    

@strawberry.field
async def achievementsByUser(uid: str, info:Info) -> List[AchievementDetails]:
    """
    Fetches list of achievements with the given userid

    Arg:
    uid (str) : The id of the user whose achievements are to be fetched.
    info (otypes.Info): The context information of user for the request.

    Returns: 
    (List[otypes.AchievementDetails]): A list of Achievements which matches the userid

    """
    user = info.context.user

    curr_user = await get_user(uid, info.context.cookies)

    if curr_user is None:
        raise Exception("User with given id does not exist")

    if (user is not None and user["role"] in ["cc", "slo"]):
        achievements = await achievementsdb.find(
            {"userids": uid}
        ).to_list(None)
    else:
        achievements = await achievementsdb.find(
            {"userids": uid,"status.state": "approved"}
        ).to_list(None)

    return [
        AchievementDetails.from_pydantic(Achievement.model_validate(achievement))
        for achievement in achievements
    ]


#register all the queries
queries = [
    allAchievements,
    achievementById,
    achievementsByUser,
    achievementsByClub,
]