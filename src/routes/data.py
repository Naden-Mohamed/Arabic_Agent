from helpers.config import get_settings, Settings
from fastapi import APIRouter, UploadFile, Depends, status
from fastapi.responses import JSONResponse
from controllers import DataController, ProjectController
from models import ResponseStatus
import os
import aiofiles

data_router = APIRouter(
    prefix="/data",
    tags=["Data"],
)

@data_router.post("/upload/{project_id}")
async def upload_file(
    project_id: str,
    file: UploadFile,
    settings: Settings = Depends(get_settings)
):

    is_valid, response_signal = DataController().validate_file(file = file)

    if not is_valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "is_valid": is_valid,   
                "response_signal": response_signal
            }
        )

    project_dir_path = ProjectController().get_project_path(project_id=project_id)
    file_path = os.path.join(project_dir_path, file.filename)

    async with aiofiles.open(file_path, 'wb') as out_file:
        while chunk := await file.read(Settings().FILE_MAX_CHUNK_SIZE):
            await out_file.write(chunk)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "is_valid": is_valid,   
            "response_signal": ResponseStatus.FILE_UPLOADED_SUCCESSFULLY.value,
            "file_path": file_path
        }
    )


    


