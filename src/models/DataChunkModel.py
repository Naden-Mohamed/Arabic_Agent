from .BaseDataModel import BaseDataModel
from .db_schemas import data_chunks
from .Enums import DataBaseEnums
from bson.objectid import ObjectId
from pymongo import InsertOne

class  DataChunkModel(BaseDataModel):
    def __init__(self, db_client: object):
        super().__init__(db_client = db_client)
        self.collection = self.db_client[DataBaseEnums.DATABASE_NAME.value][DataBaseEnums.PROJECTS_COLLECTION.value]



    async def create_chunk(self, chunk:data_chunks):

        result = await self.collection.insert_one(chunk.dict())
        chunk.id = result.inserted_id
        return chunk
    async def get_chunk_by_id(self, chunk_id: str):
        chunk = await self.collection.find_one({"_id": ObjectId(chunk_id)})

        if chunk is None:
            return None
        
        return data_chunks(**chunk)

    async def insert_many_chunks(self, patch_size: int = 100, chunks: list = []):
        for i in range(0, len(chunks), patch_size):
            batch = chunks[i:i + patch_size]
            operations = [InsertOne(chunk.dict()) for chunk in batch]
            await self.collection.bulk_write(operations) # Bulk write instead of insert many for efficiency

        return len(chunks)

    async def delete_chunk_by_project_id(self, project_id: ObjectId):
        result = await self.collection.delete_many({"chunk_project_id": project_id})
        return result.deleted_count
