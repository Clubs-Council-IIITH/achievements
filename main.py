import strawberry

from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
from strawberry.tools import create_type

from queries import sampleQuery
from mutations import sampleMutation

# create query types
Query = create_type("Query", [sampleQuery])

# create mutation types
Mutation = create_type("Mutation", [sampleMutation])

schema = strawberry.federation.Schema(
    query=Query,
    mutation=Mutation,
)

# serve API with FastAPI router
gql_app = GraphQLRouter(schema)

app = FastAPI(
    title="CC Achievements Microservice",
    description="Handles Achievements",
)
app.include_router(gql_app, prefix="/graphql")