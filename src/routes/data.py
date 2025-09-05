from helpers.config import get_settings, Settings
from fastapi import APIRouter, UploadFile, Depends, status
from fastapi.responses import JSONResponse
from controllers import DataController, ProjectController
from models import ResponseStatus
import logging
import aiofiles

logger = logging.getLogger("uvicorn.error")

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

    data_controller = DataController()
    is_valid, response_signal = data_controller.validate_file(file = file)

    if not is_valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "is_valid": is_valid,   
                "response_signal": response_signal
            }
        )

    project_dir_path = ProjectController().get_project_path(project_id=project_id)
    file_path, file_id = data_controller.generate_unique_filepath(original_filename=file.filename, project_id=project_id)[0]

    try:
        async with aiofiles.open(file_path, 'wb') as out_file:
            while chunk := await file.read(Settings().FILE_MAX_CHUNK_SIZE):
                await out_file.write(chunk)

    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        # NOT all errors should be exposed to the user (might be sensitive)
        # log the error for just internal review
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "is_valid": False,   
                "response_signal": ResponseStatus.FILE_UPLOADED_FAILED.value,
            }
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "is_valid": is_valid,   
            "response_signal": ResponseStatus.FILE_UPLOADED_SUCCESSFULLY.value,
            "file_path": file_path
        }
    )


    


