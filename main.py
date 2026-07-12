import strawberry
from contextlib import asynccontextmanager
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
from strawberry.tools import create_type
from db import ensure_achievements_index
from queries import sampleQuery
from mutations import sampleMutation
from mtypes import PyObjectId
@asynccontextmanager
async def lifespan(app:FastAPI):
    await ensure_achievements_index()
    yield


# create query types
Query = create_type("Query", [sampleQuery])

# create mutation types
Mutation = create_type("Mutation", [sampleMutation])
PyObjectIdType = strawberry.scalar(PyObjectId, serialize=str, parse_value = lambda v: PyObjectId(v))
schema = strawberry.federation.Schema(
    query=Query,
    mutation=Mutation,
    scalar_overrides={PyObjectId: PyObjectIdType}
)



# serve API with FastAPI router
gql_app = GraphQLRouter(schema)
app = FastAPI(
    title="CC Achievements Microservice",
    description="Handles Achievements",
    lifespan= lifespan
)
app.include_router(gql_app, prefix="/graphql")