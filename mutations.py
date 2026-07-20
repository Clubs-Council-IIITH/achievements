from otypes import (
    Info, 
    CreateAchievementDetails,
    EditAchievementDetails,
    AchievementDetails,
)
from mtypes import (
    Achievement_Status_State
)
from utils import (
    get_club,
    get_user
)
from fastapi.encoders import jsonable_encoder
from datetime import datetime
from models import Achievement
import strawberry
from db import achievementsdb
from utils import TIMEZONE

@strawberry.mutation
async def createAchievement(details: CreateAchievementDetails, info: Info) -> AchievementDetails:
    
    user = info.context.user
    # check if user is authenticated and has enough permissions
    if (not user or
        user['role'] not in ['club', 'slo', 'cc'] or
        (user['role']=='club' and user['uid'] not in details.clubids)):
        raise Exception("You are not authorized to  edit this achievement")
    
    if(len(details.userids)==0):
        raise Exception("User ids cannot be left empty")
    
    if(len(details.clubids)==0):
        raise Exception("Clubids cannot be left empty")
    #checks to identify if all the clubids are valid
    for club_id in details.clubids:
        club = await get_club(club_id, cookies= info.context.cookies)
        if(len(club.keys())==0):
            raise Exception("Invalid Club id")
    
    # checks to identify if all user ids are valid
    for user_id in details.userids:
        user_result = await get_user(user_id, cookies=info.context.cookies)
        if(not user_result or len(user_result.keys())==0):
            raise Exception("invalid user id")
        
    
    #checks to identify if starting date is lower or equal to ending date
    if(details.dateperiod[0]> details.dateperiod[1]):
        raise Exception("Starting date is greater than ending date")
    achievements_instance = Achievement(name= details.name, 
                                        clubids=details.clubids, 
                                        achievement_type=details.achievement_type, 
                                        userids=details.userids,
                                        content= details.content, 
                                        blog_links=details.blog_links,
                                        image_links=details.image_links,
                                        dateperiod=details.dateperiod)
    achievements_instance.status.submission_datetime = datetime.now(TIMEZONE)
    #if cc or slo, achievement is approved
   
    if user["role"] in ["slo", "cc"]:
        achievements_instance.status.state = Achievement_Status_State.approved
        achievements_instance.status.approved_datetime = achievements_instance.status.submission_datetime
        achievements_instance.status.approved_by = user['uid']
    else:
        achievements_instance.status.state = Achievement_Status_State.pending



    created_id = (
        await achievementsdb.insert_one(jsonable_encoder(achievements_instance))
    ).inserted_id
    created_achievement = Achievement.model_validate(
        (await achievementsdb.find_one({"_id": created_id}))
        )
    return AchievementDetails.from_pydantic(created_achievement)
    

@strawberry.mutation
async def editAchievement(details:EditAchievementDetails, info:Info) -> AchievementDetails:
    user = info.context.user 
    if not user:
        raise Exception("You are not authenticated")
    #check if appropriate achievement even exists
    with open("logs.txt", "w") as f:
        f.write(str(type(details.id))+ str(details.id))
    current_ref = await achievementsdb.find_one({"_id": str(details.id)})
    if not current_ref:
        raise Exception("No achievement with that particular id")
    if current_ref["status"]["state"] == "deleted":
        raise Exception("Deleted achievements cannot be edited")
    elif current_ref["status"]["state"] =="rejected":
        raise Exception("Rejected achievements cannot be edited")
    
    #check if user has appropriate permissions
    if user["role"] not in ["slo", "cc"]:
        raise Exception("You are not authorized to  edit this achievement")
    if details.dateperiod is not None:
        if(details.dateperiod[0]>details.dateperiod[1]):
            raise Exception("Starting date is greater than ending date")
    
    #check if new clubids are valid
    if details.clubids is not None:
        for club_id in details.clubids:
            club = await get_club(club_id, cookies= info.context.cookies)
            if(len(club.keys())==0):
                raise Exception("Invalid Club id")
        
    #checks to identify if all user ids are valid
    if details.userids is not None:
        for user_id in details.userids:
            user_result = await get_user(user_id, cookies=info.context.cookies)
            if(not user_result or len(user_result.keys())==0):
                raise Exception("invalid user id")
        
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
    updates["status.last_updated_datetime"] = datetime.now(TIMEZONE)
    updates["status.last_updated_by"] = user["uid"]
    query = {"_id": str(details.id)}
    updation = {"$set": updates}

    updated_ref = await achievementsdb.update_one(query, updation)
    if updated_ref.matched_count == 0:
        raise Exception("Update failed") 
    achievement_ref = await achievementsdb.find_one({"_id": str(details.id)})
    return AchievementDetails.from_pydantic(Achievement.model_validate(achievement_ref))


@strawberry.mutation
async def deleteAchievement(achievement_id:str,info:Info) ->AchievementDetails:
    """
    Mutation for deleting achievement
    """
    user = info.context.user
    if not user:
        raise Exception("You are not authenticated")

    if user["role"] not in ["slo", "cc"]:
        raise Exception("You do not have the permissions to delete an achievement")

    query = {"_id": achievement_id}
    current_ref = await achievementsdb.find_one(query)
    if not current_ref:
        raise Exception("Achievement not found")
    if current_ref["status"]["state"]=="deleted":
        raise Exception("Achievement was already deleted")
    
    updates = {"status.state": Achievement_Status_State.deleted, "status.deletion_datetime": datetime.now(TIMEZONE), "status.deleted_by": user["uid"]}
    updation = {"$set": updates}
    updated_ref = await achievementsdb.update_one(query, updation)
    if not updated_ref or updated_ref.matched_count==0:
        raise Exception("Achievement not updated in the database")
    achievement_ref = await achievementsdb.find_one(query)
    return AchievementDetails.from_pydantic(Achievement.model_validate(achievement_ref))


@strawberry.mutation
async def approveAchievement(achievement_id: str, info:Info) -> AchievementDetails:
    """
    Mutation for approving achievement
    """
    user = info.context.user
    if not user:
        raise Exception("You are not authenticated")
    if user["role"] not in ["slo", "cc" ]:
        raise Exception("You do not have the permissions to do this change")
    query = {"_id": achievement_id}
    current_ref = await achievementsdb.find_one(query)
    
    if not current_ref:
        raise Exception("Achievement does not exist")
    if current_ref["status"]["state"] =="deleted":
        raise Exception("Deleted achievements cannot be approved")
    elif current_ref["status"]["state"] =="approved":
        raise Exception("Achievement has already been approved")
    
    updates = {"status.state": Achievement_Status_State.approved, "status.approved_datetime": datetime.now(TIMEZONE), "status.approved_by": user["uid"], "status.rejected_by": None, "status.rejected_datetime": None }
    updation = {"$set":updates}

    updated_ref = await achievementsdb.update_one(query, updation)
    if not updated_ref or updated_ref.matched_count==0:
        raise Exception("Achievement not updated in the database")
    achievement_ref = await achievementsdb.find_one(query)
    return AchievementDetails.from_pydantic(Achievement.model_validate(achievement_ref))


@strawberry.mutation
async def rejectAchievement(achievement_id:str, info:Info) -> AchievementDetails:
    """
    Mutation for rejecting achievements by SLO or cc
    """
    user = info.context.user
    if not user:
        raise Exception("You are not authenticated")
    if user["role"] not in ["slo", "cc" ]:
        raise Exception("You do not have the permissions to do this change")
    query = {"_id": achievement_id}
    current_ref = await achievementsdb.find_one(query)
    
    if not current_ref:
        raise Exception("Achievement does not exist")
    if current_ref["status"]["state"] =="deleted":
        raise Exception("Deleted achievements cannot be rejected")
    elif current_ref["status"]["state"] == "approved":
        raise Exception("Approved achievements cannot be rejected")
    elif current_ref["status"]["state"] == "rejected":
        raise Exception("Achievement has already been rejected")
    
    updates = {"status.state": Achievement_Status_State.rejected, "status.rejected_datetime": datetime.now(TIMEZONE), "status.rejected_by": user["uid"]}
    updation = {"$set": updates}

    updated_ref = await achievementsdb.update_one(query, updation)
    if not updated_ref or updated_ref.matched_count==0:
        raise Exception("Achievement not updated in the database")
    achievement_ref = await achievementsdb.find_one(query)
    return AchievementDetails.from_pydantic(Achievement.model_validate(achievement_ref))

Mutations= [rejectAchievement, approveAchievement, createAchievement, deleteAchievement, editAchievement ]