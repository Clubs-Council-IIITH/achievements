import strawberry
from contextlib import asynccontextmanager
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
from strawberry.tools import create_type
from db import ensure_achievements_index
from queries import queries
from otypes import Context
from mutations import (
  Mutations
)
from mtypes import PyObjectId

@asynccontextmanager
async def lifespan(app:FastAPI):
    await ensure_achievements_index()
    yield

async def get_context() -> Context:
    return Context()

# create query types
Query = create_type("Query", queries)

# create mutation types
Mutation = create_type("Mutation", Mutations)
PyObjectIdType = strawberry.scalar(PyObjectId, serialize=str, parse_value = lambda v: PyObjectId(v))
schema = strawberry.federation.Schema(
    query=Query,
    mutation=Mutation,
    scalar_overrides={PyObjectId: PyObjectIdType}
)


# serve API with FastAPI router
gql_app = GraphQLRouter(schema, context_getter= get_context)
app = FastAPI(
    title="CC Achievements Microservice",
    description="Handles Achievements",
    lifespan= lifespan
)
app.include_router(gql_app, prefix="/graphql")