import strawberry 
from models import Achievement



@strawberry.experimental.pydantic.type(model=Achievement, all_fields=True)
class Achievement_Details:
    """
    Type for returning all the details of an achievement
    """
    pass