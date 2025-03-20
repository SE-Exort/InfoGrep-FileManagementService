from Backends.backend import Backend
from fastapi import UploadFile
from fastapi.responses import FileResponse
import os;

#this backend does not allow the FMS to be scalable. Should only be used when there is 1 replica
class FileSystem(Backend):
    def __init__(self, param):
        self.param = param
        os.makedirs(self.param, exist_ok=True);
        return;

    async def save_file(self, file_uuid: str, uploadedfile: UploadFile):
        with open(self.param + file_uuid, "wb") as file:
            content = await uploadedfile.read()  # async read chunk
            file.write(content)  # async write chunk
        return;

    def delete_file(self, file_uuid: str):
        os.remove(self.param + file_uuid);
        return;

    def get_file(self, file_uuid: str, file_name: str):
        return FileResponse(path=self.param + file_uuid, filename=file_name);
