from helpers.config import get_settings, Settings
from fastapi import APIRouter, UploadFile, Depends, status
from fastapi.responses import JSONResponse
from controllers import DataController, ProjectController, ProcessController
from models import ResponseStatus
import logging
import aiofiles
from .schemas.data_schema import DataSchema

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
    file_path, file_id = data_controller.generate_unique_filepath(original_filename=file.filename, project_id=project_id)

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
            "file_path": file_path,
            "file_id": file_id
        }
    )


@data_router.post("/process/{project_id}")
async def process_file(project_id: str, data: DataSchema):
   
    file_id = data.file_id
    chunk_size = data.chunk_size
    chunk_overlap = data.chunk_overlap_size

    process_controller = ProcessController(project_id=project_id)
    file_content = process_controller.get_file_content(file_id=file_id)
    file_chunks = process_controller.process_file_content(file_id=file_id, file_content=file_content, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    if file_chunks is None or len(file_chunks) == 0:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "is_valid": False,   
                "response_signal": ResponseStatus.PROCESSING_FAILED.value,
                "file_id": file_id
            }
        )
    return file_chunks

    


