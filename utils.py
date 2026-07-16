from typing import List

from httpx import AsyncClient

async def get_club(cid, cookies=None) -> dict | None:
    """
    This function makes a query to the Clubs service resolved by the 
    club method, fetches info about a club.

    Args:
        cid (str): club id
        cookies (dict): cookies. Defaults to None.

    Returns:
        (dict|None): response of the request

    """

    try:
        query = """
            query GetClub($clubInput: SimpleClubInput!) {
                club(clubInput: $clubInput) {
                    cid
                }
            }
        """
        variables = {
            "clubInput": {
                "cid": cid
            }
        }
        async with AsyncClient(cookies=cookies) as client:
            response = await client.post(
                "http://gateway/graphql",
                json={"query": query, "variables": variables}
            )
        return response.json()["data"]["club"]
    
    except Exception:
        return None
    

async def get_user(uid, cookies=None) -> dict | None:
    """
    This function makes a query to the Users service resolved by the
    user method, fetches info about a user

    Args:
        uid (str): user id
        cookies (dict): cookies. Default to None

    Returns:
        (dict|None): response of the request

    """

    try:
        query = """
            query GetUser($userInput: UserInput!) {
                userProfile(userInput: $userInput) {
                    uid
                }
            }
        """
        variables = {
            "userInput": {
                "uid": uid
            }
        }
        async with AsyncClient(cookies=cookies) as client:
            response = await client.post(
                "http://gateway/graphql",
                json={"query": query, "variables": variables}
            )
        result = response.json()
        print(result)
        return result["data"]["userProfile"]

    except Exception:
        return None