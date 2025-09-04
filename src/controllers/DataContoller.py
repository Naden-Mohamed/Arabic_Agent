from .BaseController import BaseController
from .ProjectContoller import ProjectController
from fastapi import UploadFile
from models import ResponseStatus
import re, os


class DataController(BaseController):
        def __init__(self):
            super().__init__()
            self.size_scale = 1048576 # convert MB to bytes

        def validate_file(self, file: UploadFile) -> bool:
            if file.content_type not in self.settings.FILE_ALLOWED_TYPES:
                return False, ResponseStatus.FILE_TYPE_NOT_SUPPORTED.value
            
            if file.size > self.settings.FILE_MAX_SIZE * self.size_scale:
                return False, ResponseStatus.FILE_SIZE_EXCEEDED.value
            
            return True, ResponseStatus.FILE_VALIDATION_PASSED.value
        

            
        def generate_unique_filename(self, original_filename: str, project_id: str):
             random_key = self.generate_random_string()
             project_path = ProjectController().get_project_path(project_id=project_id)
             clean_file_name = self.get_clean_file_name(original_filename)

             new_file_path = os.path.join(project_path, random_key + "_" + clean_file_name)

             while os.path.exists(new_file_path):
                    random_key = self.generate_random_string()
                    new_file_path = os.path.join(project_path, random_key + "_" + clean_file_name)

             return new_file_path, random_key + "_" + clean_file_name


        def get_clean_file_name(self, orig_file_name: str):

            # remove any special characters, except underscore and .
            cleaned_file_name = re.sub(r'[^\w.]', '', orig_file_name.strip())

            # replace spaces with underscore
            cleaned_file_name = cleaned_file_name.replace(" ", "_")

            return cleaned_file_name
