from fastapi import FastAPI
from routes import base, data
from motor.motor_asyncio import AsyncIOMotorClient
from helpers.config import get_settings

app = FastAPI()

settings = get_settings()
db_client = AsyncIOMotorClient(settings.MONGODB_URI)
db_name = db_client[settings.MONGODB_DB_NAME]
@app.on_event("startup")
async def startup_db_client():
    app.mongodb_client = db_client
    app.mongodb = db_name
    print("Connected to the MongoDB database!")

@app.on_event("shutdown")
async def shutdown_db_client():
    app.mongodb_client.close()
    print("Disconnected from the MongoDB database!")


@app.post("/store")
async def store_data(item: dict):
    result = await db_name.insert_one(item)
    return {"inserted_id": str(result.inserted_id)}

app.include_router(base.base_router)  
app.include_router(data.data_router)  
