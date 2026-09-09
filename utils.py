import html
import os
import re
import secrets
from datetime import datetime
from zoneinfo import ZoneInfo

from httpx import AsyncClient

TIMEZONE = ZoneInfo("Asia/Kolkata")

inter_communication_secret = os.getenv("INTER_COMMUNICATION_SECRET")


async def get_user(uid, cookies=None) -> dict | None:
    """
    Function makes a query to the Users service resolved by the userProfile
    method, fetches info about a user.

    Args:
        uid (str): user id
        cookies (dict): cookies. Defaults to None.

    Returns:
        (dict | None):userProfile
    """

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


async def get_clubs(cookies=None) -> list[dict]:
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
                "http://gateway/graphql",
                json={"query": query, "variables": variables},
            )
        return response.json()["data"]["club"]
    except Exception:
        return {}


async def get_role_emails(role: str) -> list[str]:
    """
    Brings all the emails of members belonging to a role

    Args:
        role: role of the user to be searched

    Returns:
        (List[str]): list of emails.
    """

    try:
        query = """
            query Query($role: String!, $interCommunicationSecret: String) {
              usersByRole(role: $role, interCommunicationSecret: $interCommunicationSecret) {
                uid
              }
            }
        """  # noqa: E501
        variables = {
            "role": role,
            "interCommunicationSecret": inter_communication_secret,
        }
        async with AsyncClient() as client:
            response = await client.post(
                "http://gateway/graphql",
                json={"query": query, "variables": variables},
            )
            uids = [
                user["uid"] for user in response.json()["data"]["usersByRole"]
            ]
            emails = []
            for uid in uids:
                query = """
                    query UserProfile($userInput: UserInput) {
                      userProfile(userInput: $userInput) {
                        email
                      }
                    }
                """
                variables = {"userInput": {"uid": uid}}
                resp = await client.post(
                    "http://gateway/graphql",
                    json={"query": query, "variables": variables},
                )
                emails.append(resp.json()["data"]["userProfile"]["email"])
        return emails
    except Exception:
        return []


async def get_club_details(
    clubid: str,
    cookies,
) -> dict:
    """
    This method makes a query to the clubs service resolved by the club
    method, used to get a club's name from its clubid.

    Args:
        clubid (str): club id
        cookies (dict): cookies

    Returns:
        (List[dict]): response of the request
    """

    try:
        query = """
                    query Club($clubInput: SimpleClubInput!) {
                        club(clubInput: $clubInput) {
                            cid
                            name
                            email
                            category
                        }
                    }
                """
        variable = {"clubInput": {"cid": clubid}}
        async with AsyncClient(cookies=cookies) as client:
            response = await client.post(
                "http://gateway/graphql",
                json={"query": query, "variables": variable},
            )
        return response.json()["data"]["club"]
    except Exception:
        return {}


async def get_achievement_code(submissiontime: datetime) -> str:
    """
    generate achievement code based on submission time and date

    Args:
        submissiontime(datetime): time of submitting the achievement

    Returns:
        (str): event code in the format YYYYMMDDHHMMSSXXXX
    """

    event_code_suffix = secrets.token_hex(2).upper()
    event_code_prefix = submissiontime.strftime("%Y%m%d%H%M%S")
    return f"{event_code_prefix}{event_code_suffix}"  # YYYYMMDDHHSSXXXX


def get_achievement_link(code) -> str:
    """
    Produces a link to the event page based on the event code.

    Args:
        code (str): achievement code

    Returns:
        (str): link to the achievement page
    """
    host = os.environ.get("HOST", "http://localhost")
    return f"{host}/manage/achievements/code/{code}"


# method used to convert text to html
def convert_to_html(text) -> str:
    """
    Method used to convert text to html.

    Args:
        text (str): text to be converted to html.

    Returns:
        (str): text in the form of html.
    """
    # Escape HTML special characters
    text = html.escape(text)

    # Replace URLs with HTML link tags
    url_pattern = r"(http[s]?://\S+)"
    text = re.sub(url_pattern, r'<a href="\1">\1</a>', text)

    # Replace newlines with <br> tags
    text = re.sub(r"\n", "<br>", text)

    # Replace multiple spaces with &nbsp; (non-breaking space)
    text = re.sub(r" {2,}", lambda m: "&nbsp;" * len(m.group(0)), text)

    return f"<pre>{text}</pre>"
