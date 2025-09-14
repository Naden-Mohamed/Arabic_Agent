from helpers.config import get_settings, Settings
from fastapi import APIRouter, UploadFile, Depends, status, Request
from fastapi.responses import JSONResponse
from controllers import DataController, ProjectController, ProcessController
from models import ResponseStatus
import logging
import aiofiles
from .schemas.data_schema import DataSchema
from models.ProjectModel import ProjectModel
from models.DataChunkModel import DataChunkModel
from models.db_schemas import DataChunk, Asset
from models.AssetModel import AssetModel



logger = logging.getLogger("uvicorn.error")

data_router = APIRouter(
    prefix="/data",
    tags=["Data"],
)

@data_router.post("/upload/{project_id}")
async def upload_file(
    request: Request, # this store all info about each request used to access app state exsit in main if needed 
    project_id: str,
    file: UploadFile,
    settings: Settings = Depends(get_settings)
):
    # If project_id wasn't given, create one
    project_model = await ProjectModel.create_instance(db_client=request.app.mongodb_client)
    project = await project_model.get_project_or_create_one(project_id=project_id)


    # Validate file properties
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
    
    asset_model = await AssetModel.create_instance(db_client=request.app.mongodb_client)
    asset = Asset(
        asset_project_id=project.id,
        asset_type=file.content_type,
        asset_name=file.filename,
        asset_size= await data_controller.get_file_size(file_path=file_path),
        asset_config= {
            "file_path": file_path,
            "file_id": file_id
        }
    )
    asset_record = await asset_model.create_asset(asset=asset)
    
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            # "is_valid": is_valid,   
            "response_signal": ResponseStatus.FILE_UPLOADED_SUCCESSFULLY.value,
            # "file_path": file_path,
            "file_id": str(asset_record.id),
            "project_id" : str(asset_record.asset_project_id )#don't expose yourself
        }
    )


@data_router.post("/process/{project_id}")
async def process_file(request: Request,project_id: str, data: DataSchema):
   
    file_id = data.file_id
    chunk_size = data.chunk_size
    chunk_overlap = data.chunk_overlap_size
    do_reset = data.do_reset

    project_model = await ProjectModel.create_instance(db_client=request.app.mongodb_client)
    project = await project_model.get_project_or_create_one(project_id=project_id)

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
    
    file_chunks_records = [
        DataChunk(
            chunk_text= chunk.page_content, 
            chunk_metadata= chunk.metadata,
            chunk_order= idx + 1,
            chunk_project_id= project.id,
            id = file_id
    )
        for idx, chunk in enumerate(file_chunks)
    ]

    data_chunk_model = await DataChunkModel.create_instance(db_client=request.app.mongodb_client)
    if do_reset == 1:
        _= await data_chunk_model.delete_chunk_by_project_id(project_id=project.id)

    inserted_count = await data_chunk_model.insert_many_chunks(chunks=file_chunks_records)

    return JSONResponse(
            content={  
                "response_signal": ResponseStatus.PROCESSING_SUCCESSEDED.value,
                "processed_chunks": inserted_count
            }
        )
    


