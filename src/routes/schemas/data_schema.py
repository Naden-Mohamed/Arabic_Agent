from pydantic import BaseModel
from typing import Optional

class DataSchema(BaseModel):
    file_id: str
    chunk_size: Optional[int] = 100
    chunk_overlap_size: Optional[int] = 20
    do_reset: Optional[int] = 0