from abc import ABC, abstractmethod
from fastapi import UploadFile

class Backend(ABC):
    def __init__(self, param):
        return;

    @abstractmethod
    async def save_file(self, file_uuid: str, uploadedfile: UploadFile):
        pass;

    @abstractmethod
    def delete_file(self, file_uuid: str):
        pass;

    @abstractmethod
    def get_file(self, file_uuid: str, file_name: str):
        pass;
