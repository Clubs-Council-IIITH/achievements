from graphql import GraphQLError

"""
Queries for achievements
"""

import strawberry

from db import achievementsdb
from models import Achievement
from mtypes import Achievement_Status_State
from otypes import AchievementDetails, Info
from utils import get_club


@strawberry.field
async def allAchievements(info: Info) -> list[AchievementDetails]:
    """
    Fetches all the achievements

    Args:
        info (otypes.Info): User metadata and cookies.

    Returns
        (List[otypes.AchievementDetails]): A list of all Achievements
    """
    user = info.context.user
    user_role = user.get("role") if isinstance(user, dict) else None

    if user_role in ["cc", "slo"]:
        achievements = await achievementsdb.find().to_list(length=None)
    else:
        achievements = await achievementsdb.find(
            {"status.state": "approved"}
        ).to_list(length=None)

    return [
        AchievementDetails.from_pydantic(
            Achievement.model_validate(achievement)
        )
        for achievement in achievements
    ]


@strawberry.field
async def achievementById(
    achievementid: str, info: Info
) -> AchievementDetails:
    """
    Fetches an achievement with the given id

    Args:
        achievementid (str): The id of the achievement to be fetched.
        info (otypes.Info): The context information of user for the request

    Returns:
        (otypes.AchievementDetails): Detail regarding the achievement
            with the given id

    Raises:
        Exception: Cannot access the achievement. Either you do not have
            permission to access it or it does not exist.

    """
    user = info.context.user
    user_role = user.get("role") if isinstance(user, dict) else None
    user_uid = user.get("uid") if isinstance(user, dict) else None

    achievement = await achievementsdb.find_one({"_id": achievementid})

    if achievement is None or (
        achievement["status"]["state"]
        not in {Achievement_Status_State.approved.value}
        and (
            user is None
            or (
                user_role not in {"cc", "slc", "slo"}
                and (
                    user_role != "club"
                    or (user_uid not in achievement.get("clubids", []))
                )
            )
        )
    ):
        raise GraphQLError(
            "Can not access achievement. "
            "Either it does not exist or user does not have perms."
        )

    return AchievementDetails.from_pydantic(
        Achievement.model_validate(achievement)
    )


@strawberry.field
async def achievementsByClub(cid: str, info: Info) -> list[AchievementDetails]:
    """
    Fetches list of achievements with the give clubid

    Arg:
    cid (str) : The id of the club whose achievements are to be fetched.
    info (otypes.Info): The context information of user for the request.

    Returns:
    (List[otypes.AchievementDetails]): A list of Achievements
        which matches the clubid

    """
    user = info.context.user
    user_role = user.get("role") if isinstance(user, dict) else None
    user_uid = user.get("uid") if isinstance(user, dict) else None

    club = await get_club(cid, info.context.cookies)

    if club is None:
        raise GraphQLError("Club with given id does not exist")

    can_access = user is not None and (
        user_role in ["cc", "slo"]
        or (user_role == "club" and user_uid == club.get("cid"))
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
        AchievementDetails.from_pydantic(
            Achievement.model_validate(achievement)
        )
        for achievement in achievements
    ]


@strawberry.field
async def achievementsByUser(uid: str, info: Info) -> list[AchievementDetails]:
    """
    Fetches list of achievements with the given userid

    Arg:
    uid (str) : The id of the user whose achievements are to be fetched.
    info (otypes.Info): The context information of user for the request.

    Returns:
    (List[otypes.AchievementDetails]): A list of Achievements
        which matches the userid

    """
    user = info.context.user
    user_role = user.get("role") if isinstance(user, dict) else None
    user_uid = user.get("uid") if isinstance(user, dict) else None

    if user_role in ["cc", "slo"]:
        achievements = await achievementsdb.find({"userids": uid}).to_list(
            None
        )
    elif user_uid == uid:
        achievements = await achievementsdb.find(
            {"userids": uid, "status.state": {"$ne": "deleted"}}
        ).to_list(None)
    else:
        achievements = await achievementsdb.find(
            {"userids": uid, "status.state": "approved"}
        ).to_list(None)

    return [
        AchievementDetails.from_pydantic(
            Achievement.model_validate(achievement)
        )
        for achievement in achievements
    ]


@strawberry.field
async def achievementid(code: str, info: Info) -> str:
    """
    Returns achievementid of the achievement with given achievement code.

    Args:
        code (str): The code of the achievement to be fetched.
        info (otypes.Info): The context information of user for the request.

    Returns:
        (str): The id of the achievement with the given code.

    Raises:
        Exception: Achievement with given code does not exist
    """

    achievement = await achievementsdb.find_one({"code": code})

    if achievement is None:
        raise GraphQLError("Achievement with given code does not exist.")

    return achievement["_id"]


# register all the queries
queries = [
    allAchievements,
    achievementById,
    achievementsByUser,
    achievementsByClub,
    achievementid,
]
