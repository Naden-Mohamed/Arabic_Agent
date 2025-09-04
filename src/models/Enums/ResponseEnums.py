from enum import Enum

class ResponseStatus(Enum):
    FILE_TYPE_NOT_SUPPORTED = "File type not supported."
    FILE_SIZE_EXCEEDED = "File size exceeded."
    FILE_UPLOADED_SUCCESSFULLY = "File uploaded successfully."
    FILE_UPLOADED_FAILED = "File upload failed."
    FILE_VALIDATION_PASSED = "File validation passed."