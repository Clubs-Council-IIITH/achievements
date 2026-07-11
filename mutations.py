from strawberry.types import Info
import strawberry


@strawberry.mutation
def sampleMutation(info: Info) -> str:
    return "Sample Mutation Result"