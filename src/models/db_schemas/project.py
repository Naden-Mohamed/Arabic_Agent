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
    # if you find anything strange u don't know how to deal with just ignore it and don't raise error
        arbitrary_types_allowed = True


    @classmethod # Static method
    def get_indexes(cls):
        return [
            {
                "key": ("project_id", 1), # 1 for Ascending, -1 for Decs
                "name":"project_id_index_1",
                "unique": True # Shouldn't be repeated
            }
        ]
