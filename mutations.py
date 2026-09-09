from datetime import datetime

import strawberry
from fastapi.encoders import jsonable_encoder

from db import achievementsdb
from mailing import trigger_mail
from mailing_templates import (
    APPROVED_ACHIEVEMENT_BODY_FOR_CLUB,
    APPROVED_ACHIEVEMENT_SUBJECT,
    CREATE_ACHIEVEMENT_BODY,
    CREATE_ACHIEVEMENT_SUBJECT,
    REJECT_ACHIEVEMENT_BODY_FOR_CLUB,
    REJECT_ACHIEVEMENT_SUBJECT,
)
from models import Achievement
from mtypes import Achievement_Status_State
from otypes import (
    AchievementDetails,
    CreateAchievementDetails,
    EditAchievementDetails,
    Info,
)
from utils import (
    TIMEZONE,
    get_achievement_code,
    get_achievement_link,
    get_club,
    get_club_details,
    get_role_emails,
    get_user,
)


@strawberry.mutation
async def createAchievement(
    details: CreateAchievementDetails, info: Info
) -> AchievementDetails:
    """
    Creates an achievement
    Args:
        details(otypes.CreateAchievementDetails): contains all the fields
            required to create a new achievement
    Returns:
        (otypes.AchievementDetails): Details regarding the achievement
            with the given id
    Raises:
        You are not authenticated
        You do not have the permissions to create this achievement
        User ids cannot be left empty
        Clubids cannot be left empty
        Contains an invalid user id
        Contains an invalid club id
        Starting date is greater than ending date
        Insertion failed in the database
    """

    user = info.context.user
    # check if user is authenticated and has enough permissions
    if not user:
        raise Exception("You are not authenticated")
    if user["role"] not in ["club", "slo", "cc", "slc"] or (
        user["role"] == "club" and user["uid"] not in details.clubids
    ):
        raise Exception(
            "You do not have the permissions to create this achievement"
        )

    if len(details.userids) == 0:
        raise Exception("User ids cannot be left empty")

    if len(details.clubids) == 0:
        raise Exception("Clubids cannot be left empty")
    # checks to identify if all the clubids are valid
    for club_id in details.clubids:
        club = await get_club(club_id, cookies=info.context.cookies)
        if len(club.keys()) == 0:
            raise Exception("Contains an invalid club id")

    # checks to identify if all user ids are valid
    for user_id in details.userids:
        user_result = await get_user(user_id, cookies=info.context.cookies)
        if not user_result or len(user_result.keys()) == 0:
            raise Exception("Contains an invalid user id")

    # checks to identify if starting date is lower or equal to ending date
    if details.dateperiod[0] > details.dateperiod[1]:
        raise Exception("Starting date is greater than ending date")
    achievements_instance = Achievement(
        name=details.name,
        clubids=details.clubids,
        achievement_type=details.achievement_type,
        userids=details.userids,
        content=details.content,
        blog_links=details.blog_links,
        image_links=details.image_links,
        dateperiod=details.dateperiod,
        venue=details.venue,
    )
    achievements_instance.status.submission_datetime = datetime.now(TIMEZONE)
    # if cc or slo, achievement is approved
    code = await get_achievement_code(
        achievements_instance.status.submission_datetime
    )
    achievements_instance.code = code
    if user["role"] in ["slo", "cc"]:
        achievements_instance.status.state = Achievement_Status_State.approved
        achievements_instance.status.approved_datetime = (
            achievements_instance.status.submission_datetime
        )
        achievements_instance.status.approved_by = user["uid"]
    else:
        achievements_instance.status.state = Achievement_Status_State.pending
    try:
        created_id = (
            await achievementsdb.insert_one(
                jsonable_encoder(achievements_instance)
            )
        ).inserted_id
    except Exception:
        raise Exception("Insertion failed in the database")
    created_achievement = Achievement.model_validate(
        await achievementsdb.find_one({"_id": created_id})
    )

    ## trigger mail notification
    mail_content = created_achievement.content
    if mail_content == "":
        mail_content = "N/A"

    mail_to = []
    mail_uid = user["uid"]

    if created_achievement.status.state == Achievement_Status_State.pending:
        club = await get_club_details(mail_uid, info.context.cookies)
        mail_to = await get_role_emails("cc") + await get_role_emails("slo")
        mail_subject = CREATE_ACHIEVEMENT_SUBJECT.safe_substitute(
            achievement=created_achievement.name
        )
        mail_body = CREATE_ACHIEVEMENT_BODY.safe_substitute(
            club=club["name"],
            achievement=created_achievement.name,
            achievementlink=get_achievement_link(created_achievement.code),
            approved_by="Clubs_Council",
        )
        await trigger_mail(
            mail_uid,
            mail_subject,
            mail_body,
            toRecipients=mail_to,
            cookies=info.context.cookies,
        )
    return AchievementDetails.from_pydantic(created_achievement)


@strawberry.mutation
async def editAchievement(
    details: EditAchievementDetails, info: Info
) -> AchievementDetails:
    """
    Edits an achievement
    Args:
        details(otypes.EditAchievementDetails): All the input details to change
            and the id of the achievement to be edited
    Returns:
        (otypes.AchievementDetails): Details regarding the achievement
            with the given id
    Raises:
        You are not authenticated
        Achievement does not exist
        Deleted achievements cannot be edited
        Rejected achievements cannot be edited
        You do not have permissions to edit this achievement
        Starting date is greater than ending date
        Contains an invalid clubid
        Contains an invalid userid
        Update failed in the database
    """
    user = info.context.user
    if not user:
        raise Exception("You are not authenticated")
    # check if appropriate achievement even exists
    current_ref = await achievementsdb.find_one({"_id": str(details.id)})
    if not current_ref:
        raise Exception("Achievement does not exist")
    if current_ref["status"]["state"] == "deleted":
        raise Exception("Deleted achievements cannot be edited")
    elif current_ref["status"]["state"] == "rejected":
        raise Exception("Rejected achievements cannot be edited")

    # check if user has appropriate permissions
    if user["role"] not in ["slo", "cc", "slc"]:
        raise Exception("You do not have permissions to edit this achievement")
    if (
        details.dateperiod is not None
        and details.dateperiod[0] > details.dateperiod[1]
    ):
        raise Exception("Starting date is greater than ending date")

    # check if new clubids are valid
    if details.clubids is not None:
        for club_id in details.clubids:
            club = await get_club(club_id, cookies=info.context.cookies)
            if len(club.keys()) == 0:
                raise Exception("Contains an invalid clubid")

    # checks to identify if all user ids are valid
    if details.userids is not None:
        for user_id in details.userids:
            user_result = await get_user(user_id, cookies=info.context.cookies)
            if not user_result or len(user_result.keys()) == 0:
                raise Exception("Contains an invalid userid")

    updates = {}
    if details.name is not None:
        updates["name"] = details.name.strip()
    if details.clubids is not None:
        updates["clubids"] = details.clubids
    if details.achievement_type is not None:
        updates["achievement_type"] = details.achievement_type
    if details.userids is not None:
        updates["userids"] = details.userids
    if details.blog_links is not None:
        updates["blog_links"] = details.blog_links
    if details.content is not None:
        updates["content"] = details.content
    if details.image_links is not None:
        updates["image_links"] = details.image_links
    if details.dateperiod is not None:
        updates["dateperiod"] = details.dateperiod
    if details.venue is not None:
        updates["venue"] = details.venue
    updates["status.last_updated_datetime"] = datetime.now(TIMEZONE)
    updates["status.last_updated_by"] = user["uid"]
    query = {"_id": str(details.id)}
    updation = {"$set": updates}
    updation = jsonable_encoder(updation)

    updated_ref = await achievementsdb.update_one(query, updation)
    if updated_ref.matched_count == 0:
        raise Exception("Update failed in the database")
    achievement_ref = await achievementsdb.find_one({"_id": str(details.id)})
    return AchievementDetails.from_pydantic(
        Achievement.model_validate(achievement_ref)
    )


@strawberry.mutation
async def deleteAchievement(
    achievement_id: str, info: Info
) -> AchievementDetails:
    """
    Deletes achievement
    Args:
        achievement_id(str):id of achievement to be deleted
    Returns:
        (otypes.AchievementDetails): Details regarding the achievement
            with the given id
    Raises:
        You are not authenticated
        You do not have the permissions to delete an achievement
        Achievement not found
        Achievement was already deleted
        Achievement not updated in the database
    """
    user = info.context.user
    if not user:
        raise Exception("You are not authenticated")

    if user["role"] not in ["slo", "cc", "slc"]:
        raise Exception(
            "You do not have the permissions to delete an achievement"
        )

    query = {"_id": achievement_id}
    current_ref = await achievementsdb.find_one(query)
    if not current_ref:
        raise Exception("Achievement not found")
    if current_ref["status"]["state"] == "deleted":
        raise Exception("Achievement was already deleted")

    updates = {
        "status.state": Achievement_Status_State.deleted,
        "status.deletion_datetime": datetime.now(TIMEZONE),
        "status.deleted_by": user["uid"],
    }
    updation = {"$set": updates}
    updated_ref = await achievementsdb.update_one(query, updation)
    if not updated_ref or updated_ref.matched_count == 0:
        raise Exception("Achievement not updated in the database")
    achievement_ref = await achievementsdb.find_one(query)
    return AchievementDetails.from_pydantic(
        Achievement.model_validate(achievement_ref)
    )


@strawberry.mutation
async def approveAchievement(
    achievement_id: str, info: Info
) -> AchievementDetails:
    """
    Approves achievement
    Args:
        achievement_id(str): id of achievement to be approved
    Returns:
        (otypes.AchievementDetails): Details regarding the achievement
            with the given id
    Raises:
        You are not authenticated
        You do not have the permissions to do this change
        Achievement does not exist
        Deleted achievements cannot be approved
        Achievement has already been approved
        Achievement not updated in the database
    """
    user = info.context.user
    if not user:
        raise Exception("You are not authenticated")
    if user["role"] not in ["slo", "cc", "slc"]:
        raise Exception("You do not have the permissions to do this change")
    query = {"_id": achievement_id}
    current_ref = await achievementsdb.find_one(query)

    if not current_ref:
        raise Exception("Achievement does not exist")
    if current_ref["status"]["state"] == "deleted":
        raise Exception("Deleted achievements cannot be approved")
    elif current_ref["status"]["state"] == "approved":
        raise Exception("Achievement has already been approved")

    achievement = Achievement.model_validate(current_ref)

    club_emails = []
    club_names = []

    for club_id in achievement.clubids:
        club = await get_club_details(club_id, info.context.cookies)
        if not club:
            raise Exception("Club does not exist.")
        club_emails.append(club["email"])
        club_names.append(club["name"])

    updates = {
        "status.state": Achievement_Status_State.approved,
        "status.approved_datetime": datetime.now(TIMEZONE),
        "status.approved_by": user["uid"],
        "status.rejected_by": None,
        "status.rejected_datetime": None,
    }
    updation = {"$set": updates}

    updated_ref = await achievementsdb.update_one(query, updation)
    if not updated_ref or updated_ref.matched_count == 0:
        raise Exception("Achievement not updated in the database")
    achievement_ref = await achievementsdb.find_one(query)

    if achievement.status.state != Achievement_Status_State.approved:
        if user["role"] == "cc":
            mail_to = club_emails
            mail_subject = APPROVED_ACHIEVEMENT_SUBJECT.safe_substitute(
                achievement_id=achievement.code,
                achievement=achievement.name,
            )
            mail_body = APPROVED_ACHIEVEMENT_BODY_FOR_CLUB.safe_substitute(
                clubs=club_names,
                achievement=achievement.name,
                achievementlink=get_achievement_link(achievement.code),
                approved_by="Clubs_Council",
            )
            await trigger_mail(
                user["uid"],
                mail_subject,
                mail_body,
                toRecipients=mail_to,
                cookies=info.context.cookies,
            )

        elif user["role"] == "slo":
            mail_to = club_emails
            cc_to = await get_role_emails("cc")
            mail_subject = APPROVED_ACHIEVEMENT_SUBJECT.safe_substitute(
                achievement_id=achievement.code,
                achievement=achievement.name,
            )
            mail_body = APPROVED_ACHIEVEMENT_BODY_FOR_CLUB.safe_substitute(
                achievement=achievement.name,
                achievementlink=get_achievement_link(achievement.code),
                approved_by="Student Life Office",
            )
            await trigger_mail(
                user["uid"],
                mail_subject,
                mail_body,
                toRecipients=mail_to,
                ccRecipients=cc_to,
                cookies=info.context.cookies,
            )
    return AchievementDetails.from_pydantic(
        Achievement.model_validate(achievement_ref)
    )


@strawberry.mutation
async def rejectAchievement(
    achievement_id: str, info: Info
) -> AchievementDetails:
    """
    Rejects an achievement
    Args:
        achievement_id(str): unique id of the achievement to be rejected
    Returns:
        (otypes.AchievementDetails): Details regarding the achievement
            with the given id

    Raises:
        You are not authenticated
        You do not that the permissions to do this change
        Achievement does not exist
        Deleted achievements cannot be rejected
        Approved achievements cannot be rejected
        Achievement has already been rejected
        Achievement not updated in database
    """
    user = info.context.user
    if not user:
        raise Exception("You are not authenticated")
    if user["role"] not in ["slo", "cc", "slc"]:
        raise Exception("You do not have the permissions to do this change")
    query = {"_id": achievement_id}
    current_ref = await achievementsdb.find_one(query)

    if not current_ref:
        raise Exception("Achievement does not exist")
    if current_ref["status"]["state"] == "deleted":
        raise Exception("Deleted achievements cannot be rejected")
    elif current_ref["status"]["state"] == "approved":
        raise Exception("Approved achievements cannot be rejected")
    elif current_ref["status"]["state"] == "rejected":
        raise Exception("Achievement has already been rejected")

    achievement = Achievement.model_validate(current_ref)

    club_emails = []
    club_names = []

    for club_id in achievement.clubids:
        club = await get_club_details(club_id, info.context.cookies)
        if not club:
            raise Exception("Club does not exist.")
        club_emails.append(club["email"])
        club_names.append(club["name"])

    updates = {
        "status.state": Achievement_Status_State.rejected,
        "status.rejected_datetime": datetime.now(TIMEZONE),
        "status.rejected_by": user["uid"],
    }
    updation = {"$set": updates}

    updated_ref = await achievementsdb.update_one(query, updation)
    if not updated_ref or updated_ref.matched_count == 0:
        raise Exception("Achievement not updated in the database")
    achievement_ref = await achievementsdb.find_one(query)

    if achievement.status.state != Achievement_Status_State.rejected:
        if user["role"] == "cc":
            mail_to = club_emails
            mail_subject = REJECT_ACHIEVEMENT_SUBJECT.safe_substitute(
                achievement_id=achievement.code,
                achievement=achievement.name,
            )
            mail_body = REJECT_ACHIEVEMENT_BODY_FOR_CLUB.safe_substitute(
                clubs=club_names,
                achievement=achievement.name,
                achievementlink=get_achievement_link(achievement.code),
                rejected_by="Clubs_Council",
            )
            await trigger_mail(
                user["uid"],
                mail_subject,
                mail_body,
                toRecipients=mail_to,
                cookies=info.context.cookies,
            )

        elif user["role"] == "slo":
            mail_to = club_emails
            cc_to = await get_role_emails("cc")
            mail_subject = REJECT_ACHIEVEMENT_SUBJECT.safe_substitute(
                achievement_id=achievement.code,
                achievement=achievement.name,
            )
            mail_body = REJECT_ACHIEVEMENT_BODY_FOR_CLUB.safe_substitute(
                clubs=club_names,
                achievement=achievement.name,
                achievementlink=get_achievement_link(achievement.code),
                rejected_by="Student Life Office",
            )

            await trigger_mail(
                user["uid"],
                mail_subject,
                mail_body,
                toRecipients=mail_to,
                ccRecipients=cc_to,
                cookies=info.context.cookies,
            )
    return AchievementDetails.from_pydantic(
        Achievement.model_validate(achievement_ref)
    )


Mutations = [
    rejectAchievement,
    approveAchievement,
    createAchievement,
    deleteAchievement,
    editAchievement,
]
