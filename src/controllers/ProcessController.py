from .BaseController import BaseController
from .ProjectContoller import ProjectController
import os
from langchain_community.document_loaders import TextLoader, PyPDFLoader, UnstructuredWordDocumentLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from models import ProcessingEnums


class ProcessController(BaseController):
    def __init__(self, project_id: str):
        super().__init__()
        self.project_id = project_id
        self.project_path = ProjectController().get_project_path(project_id=project_id) 

    def get_file_extension(self, file_id: str):

        return os.path.splitext(file_id)[-1]

    def get_loader_by_extension(self, file_id: str):
        file_extension = self.get_file_extension(file_id=file_id).lower()
        file_path = os.path.join(self.project_path, file_id)

        if file_extension == ProcessingEnums.TEXT.value:
            return TextLoader(file_path, encoding='utf8')
        elif file_extension == ProcessingEnums.PDF.value:
            return PyPDFLoader(file_path)
        elif file_extension in ProcessingEnums.WORD.value:
            return UnstructuredWordDocumentLoader(file_path)
        else:
            return None
        

    def get_file_content(self, file_id: str):
        loader = self.get_loader_by_extension(file_id=file_id)
        if loader is None:
            return None

        return loader.load()
    
    def process_file_content(self, file_id: str, file_content: list, chunk_size: int = 1000, chunk_overlap: int = 200):

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        file_content_texts = [doc.page_content for doc in file_content]
        file_content_metadata = [doc.metadata for doc in file_content]
        chunks = text_splitter.create_documents(file_content_texts, metadatas = file_content_metadata)

        return chunks