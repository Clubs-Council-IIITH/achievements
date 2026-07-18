from httpx import AsyncClient
from typing import List
from zoneinfo import ZoneInfo

TIMEZONE = ZoneInfo("Asia/Kolkata")

async def get_user(uid, cookies=None) -> dict | None:
    """
    Function makes a query to the Users service resolved by the userProfile
    method, fetches info about a user.

    Args:
        uid (str): user id
        cookies (dict): cookies. Defaults to None.

    Returns:
        (dict | None):userProfile
    """  # noqa: E501

    try:
        query = """
            query GetUserProfile($userInput: UserInput!) {
                userProfile(userInput: $userInput) {
                    firstName
                    lastName
                    email
                    rollno
                }
            }
        """
        variable = {"userInput": {"uid": uid}}
        async with AsyncClient(cookies=cookies) as client:
            response = await client.post(
                "http://gateway/graphql",
                json={"query": query, "variables": variable},
            )

        return response.json()["data"]["userProfile"]
    except Exception:
        return None


async def get_clubs(cookies=None) -> List[dict]:
    """
    Function to call a query to the Clubs service resolved by the allClubs
    method, fetches info about all clubs.

    Args:
        cookies (dict): cookies. Defaults to None.

    Returns:
        (List[dict]): responce of the request
    """

    try:
        query = """
                    query AllClubs {
                        allClubs {
                            cid
                            name
                            code
                            email
                        }
                    }
                """
        async with AsyncClient(cookies=cookies) as client:
            response = await client.post(
                "http://gateway/graphql", json={"query": query}
            )
        return response.json()["data"]["allClubs"]
    except Exception:
        return []
    
async def get_club(cid, cookies=None) -> dict:
    """
    Function to call a query to the Clubs service resolved by the club
    method, fetches info about a particular club with a given club id.

    Args:
        cid (str): code of the club to be fetched. 
        cookies (dict): cookies. Defaults to None.

    Returns:
        dict: response of the request
    """

    try:
        query = """
                    query Club($clubid: SimpleClubInput!) {
                        club(clubInput: $clubid) {
                            cid
                            name
                            code
                            email
                        }
                    }
                """
        variables = {"clubid": {"cid": cid}}
        async with AsyncClient(cookies=cookies) as client:
            response = await client.post(
                "http://gateway/graphql", json={"query": query, "variables": variables}
            )
        return response.json()["data"]["club"]
    except Exception:
        return {}
