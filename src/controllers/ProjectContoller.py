from fastapi import UploadFile
from .BaseController import BaseController
from models import ResponseStatus
import os

class ProjectController(BaseController):
    def __init__(self):
        super().__init__()
    
    def get_project_path(self, project_id: str):
        self.project_dir = os.path.join(self.files_dir_path, project_id)
        if not os.path.exists(self.project_dir):
            os.makedirs(self.project_dir)
        return self.project_dir