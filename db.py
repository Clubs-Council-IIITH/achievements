"""
MongoDB Initialization Module.

This module sets up the connection to the MongoDB database.
It ensures that the required indexes are created.

Attributes:
    MONGO_USERNAME (str): An environment variable having MongoDB username.
                          Defaults to "username".
    MONGO_PASSWORD (str): An environment variable having MongoDB password.
                          Defaults to "password".
    MONGO_PORT (str): MongoDB port. Defaults to "27017".
    MONGO_URI (str): MongoDB URI.
    MONGO_DATABASE (str): MongoDB database name.
    client (pymongo.AsyncMongoClient): MongoDB async client.
    db (pymongo.asynchronous.database.AsyncDatabase): MongoDB database.
    achievementsdb (pymongo.asynchronous.collection.AsyncCollection): MongoDB
                                                             achievements collection.
"""
from pymongo import AsyncMongoClient
from os import getenv

MONGO_URI = "mongodb://{}:{}@mongo:{}/".format(
    getenv("MONGO_USERNAME", default="username"),
    getenv("MONGO_PASSWORD", default="password"),
    getenv("MONGO_PORT", default="27017"),
)
MONGO_DATABASE = getenv("MONGO_DATABASE", default="default")

# instantiate mongo client
client = AsyncMongoClient(MONGO_URI)

# get database
db = client[MONGO_DATABASE]
achievementsdb = db.achievements


async def ensure_achievements_index():
    try:
        if "clubids" not in (await achievementsdb.index_information()):
            await achievementsdb.create_index("clubids", name ="clubids")
        else:
            print("clubids index already exists")
        if "userids" not in (await achievementsdb.index_information()):
            await achievementsdb.create_index("userids", name = "userids")
        else:
            print("userids index already exists")
    except Exception:
        pass



