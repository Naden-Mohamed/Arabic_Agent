from helpers.config import get_settings, Settings
from fastapi import APIRouter, UploadFile, Depends, status
from fastapi.responses import JSONResponse
from controllers import DataController, ProjectController


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
    else:
        project_path = ProjectController().get_project_path(project_id=project_id)
        file_location = f"{project_path}/{file.filename}"
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "is_valid": is_valid,   
                "response_signal": response_signal,
                "file_location": file_location
                
            }  )     


