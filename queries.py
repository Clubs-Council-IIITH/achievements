from strawberry.types import Info
import strawberry


@strawberry.field
def sampleQuery(info: Info) -> str:
    return "hello"