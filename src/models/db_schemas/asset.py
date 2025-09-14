from pydantic import BaseModel, Field, validator
from typing import Optional
from bson.objectid import ObjectId
from datetime import datetime

class Asset(BaseModel):
    id: Optional[ObjectId] = Field(None, alias="_id")
    asset_project_id: ObjectId
    asset_type: str = Field(..., min_length=1)  # e.g., "image", "video", "document"
    asset_name: str = Field(..., min_length=1)   
    asset_size: int = Field(..., gt=0)  # size in bytes
    asset_config: dict = Field(default= None)  # Configuration details
    created_at: datetime = Field(default=datetime.utcnow)

    class Config:
        arbitrary_types_allowed = True
        allow_population_by_field_name = True  # lets you use "id" or "_id"

    @classmethod
    def get_indexes(cls):
        return [
            {
                "key": [("project_id", 1)],   
                "name": "project_id_index_1",
                "unique": False,
                "partialFilterExpression": {  # ✅ only enforce uniqueness if project_id exists
                    "project_id": {"$exists": True, "$ne": None}
                }
            },
            {
                "key": [("project_id", 1), ("asset_name", 1)],  
                "name": "project_id_asset_name_index_1",
                "unique": True,
                "partialFilterExpression": { 
                    "project_id": {"$exists": True, "$ne": None}
                }   
            }
        ]