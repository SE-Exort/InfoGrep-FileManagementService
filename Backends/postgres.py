import psycopg2
import io
import os;

from Backends.backend import Backend
from fastapi import UploadFile
from fastapi.responses import Response
import filemanagement
import filetype

class Postgres(Backend):
    def __init__(self, param):
        self.param = param;
        return;

    async def save_file(self, file_uuid: str, uploadedfile: UploadFile):
        file_object = await uploadedfile.read();
        self.param.backendSaveFile(file_uuid, file_object);
        return;

    def delete_file(self, file_uuid: str):
        self.param.backendDeleteFile(file_uuid);
        return;

    def get_file(self, file_uuid: str, file_name: str):
        file = self.param.backendReadFile(file_uuid);
        headers = {
            'Content-Disposition': 'attachment; filename='+file_name,
            'Content-Type': filetype.guess_mime(file.read())
        }
        file.seek(0);
        returnval = Response(file.read(), headers=headers);
        file.close();
        return returnval
