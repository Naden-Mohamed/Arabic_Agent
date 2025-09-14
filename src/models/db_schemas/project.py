from pydantic import BaseModel, Field, validator
from typing import Optional
from bson.objectid import ObjectId

class Project(BaseModel):
    id: Optional[ObjectId] = Field(None, alias="_id")
    project_id: str = Field(..., min_length=1)

    @validator('project_id')
    def validate_project_id(cls, value):
        if not value.isalnum():
            raise ValueError('project_id must be alphanumeric')
        return value

    class Config:
        arbitrary_types_allowed = True
        allow_population_by_field_name = True  # lets you use "id" or "_id"

    @classmethod
    def get_indexes(cls):
        return [
            {
                "key": [("project_id", 1)],   # ✅ correct format
                "name": "project_id_index_1",
                "unique": True,
                "partialFilterExpression": {  # ✅ only enforce uniqueness if project_id exists
                    "project_id": {"$exists": True, "$ne": None}
                }
            }
        ]
