import json;
import uuid;
import os;

from fastapi import FastAPI, APIRouter;
from fastapi import UploadFile;
from fastapi.responses import FileResponse

from authenticate import *;
from InfoGrep_BackendSDK import parse_api
import filemanagement;

import requests

router = APIRouter(prefix='/api', tags=["api"]);
filestoragedb = filemanagement.filemanagement();

@router.get('/filelist')
def get_filelist(user_uuid, chatroom_uuid, cookie):
    #authenticate user and chatroom
    #user must have a valid session cookie
    auth_user(user_uuid=user_uuid, cookie=cookie)
    auth_user_chatroom(user_uuid=user_uuid, chatroom_id=chatroom_uuid);
    #obtain the list of files in the specified chatroom as well as the file uuids
    filelist = filestoragedb.getFilesFromUserandChatroom(user_id=user_uuid,chatroom_id=chatroom_uuid);
    return filelist;

@router.get('/file')
def get_file(user_uuid, chatroom_uuid, file_uuid, cookie):
    #authenticate user and chatroom
    #user must have a valid session cookie
    auth_user(user_uuid=user_uuid, cookie=cookie)
    auth_user_chatroom(user_uuid=user_uuid, chatroom_id=chatroom_uuid);

    #verify if file exists for user_id and chatroom_id
    if filestoragedb.isValidFile(user_uuid, chatroom_uuid, file_uuid):
        return FileResponse(path='files/' + file_uuid, filename=filestoragedb.getFileName(user_uuid, chatroom_uuid, file_uuid));
    raise HTTPException(status_code=403, detail="Requested file not found");

@router.post('/file')
async def post_file(user_uuid, chatroom_uuid, uploadedfile: UploadFile, cookie):
    #authenticate user and chatroom
    #user must have a valid session cookie
    auth_user(user_uuid=user_uuid, cookie=cookie)
    auth_user_chatroom(user_uuid=user_uuid, chatroom_id=chatroom_uuid);
    if uploadedfile.size > 10*1024*1024:
        raise HTTPException(status_code=403, detail="File too large")
    #upload the file from the user into the chatroom
    file_uuid = uuid.uuid4();

    with open('files/' + str(file_uuid), "wb") as file:
        content = await uploadedfile.read()  # async read chunk
        file.write(content)  # async write chunk
    
    
    filestoragedb.createFile(user_uuid, chatroom_uuid, file_uuid, uploadedfile.filename);

    parse_api.parse_postStartParsing(user_uuid=user_uuid, chatroom_uuid=chatroom_uuid, file_uuid=file_uuid, filetype="PDF", cookie=cookie);
    return file_uuid;

@router.delete('/file')
def delete_file(user_uuid, chatroom_uuid, file_uuid, cookie):
    #authenticate user and chatroom
    #user must have a valid session cookie
    auth_user(user_uuid=user_uuid, cookie=cookie)
    auth_user_chatroom(user_uuid=user_uuid, chatroom_id=chatroom_uuid);
    #check to make sure the file the user is trying to delete is valid
    if filestoragedb.isValidFile(user_uuid, chatroom_uuid, file_uuid):
        filestoragedb.deleteFile(file_uuid);
        os.remove('files/' + file_uuid);
    else:
        raise HTTPException(status_code=403, detail="File does not exist or does not belong to the user")
    return;

