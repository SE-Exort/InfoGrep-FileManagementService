from Backends.backend import Backend
from fastapi import UploadFile
from fastapi.responses import FileResponse
import os;

class FileSystem(Backend):
    def __init__(self, location):
        self.location = location
        os.makedirs(self.location, exist_ok=True);
        return;

    async def save_file(self, file_uuid: str, uploadedfile: UploadFile):
        with open('files/' + file_uuid, "wb") as file:
            content = await uploadedfile.read()  # async read chunk
            file.write(content)  # async write chunk
        return;

    def delete_file(self, file_uuid: str):
        os.remove('files/' + file_uuid);
        return;

    def get_file(self, file_uuid: str, file_name: str):
        return FileResponse(path='files/' + file_uuid, filename=file_name);
