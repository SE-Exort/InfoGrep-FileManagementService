import json;
import uuid;
import os;

from fastapi import FastAPI, APIRouter;
from fastapi import UploadFile;
from fastapi.responses import FileResponse
from fastapi import HTTPException

from InfoGrep_BackendSDK import authentication_sdk
from InfoGrep_BackendSDK import parse_api
from InfoGrep_BackendSDK import room_sdk
import filemanagement;

import requests

router = APIRouter(prefix='/api', tags=["api"]);
filestoragedb = filemanagement.filemanagement();

@router.get('/filelist')
def get_filelist(chatroom_uuid, cookie):
    #authenticate user and chatroom
    #user must have a valid session cookie
    user_uuid;
    try:
        user_uuid = authentication_sdk.User(cookie).profile()['user_uuid'];
    except:
        raise HTTPException(status_code=401, detail="User or session cookie invalid")
    room_sdk.get_userInRoom(chatroom_uuid=chatroom_uuid, cookie=cookie);

    #obtain the list of files in the specified chatroom as well as the file uuids
    filelist = filestoragedb.getFilesFromChatroom(chatroom_uuid=chatroom_uuid);
    response = {'list': []}
    for item in filelist:
        response["list"].append({"File_UUID": item[0], "Filename": item[1]})
    return response;

@router.get('/file')
def get_file(chatroom_uuid, file_uuid, cookie):
    #authenticate user and chatroom
    #user must have a valid session cookie
    user_uuid;
    try:
        user_uuid = authentication_sdk.User(cookie).profile()['user_uuid'];
    except:
        raise HTTPException(status_code=401, detail="User or session cookie invalid")
    room_sdk.get_userInRoom(chatroom_uuid=chatroom_uuid, cookie=cookie);

    #verify if file exists for chatroom_uuid
    if filestoragedb.isValidFile(chatroom_uuid, file_uuid):
        return FileResponse(path='files/' + file_uuid, filename=filestoragedb.getFileName(chatroom_uuid, file_uuid));
    raise HTTPException(status_code=403, detail="Requested file not found");

@router.post('/file')
async def post_file(chatroom_uuid, uploadedfile: UploadFile, cookie):
    #authenticate user and chatroom
    #user must have a valid session cookie
    user_uuid;
    try:
        user_uuid = authentication_sdk.User(cookie).profile()['user_uuid'];
    except:
        raise HTTPException(status_code=401, detail="User or session cookie invalid")
    room_sdk.get_userInRoom(chatroom_uuid=chatroom_uuid, cookie=cookie);

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
def delete_file(chatroom_uuid, file_uuid, cookie):
    #authenticate user and chatroom
    #user must have a valid session cookie
    user_uuid;
    try:
        user_uuid = authentication_sdk.User(cookie).profile()['user_uuid'];
    except:
        raise HTTPException(status_code=401, detail="User or session cookie invalid")
    room_sdk.get_userInRoom(chatroom_uuid=chatroom_uuid, cookie=cookie);

    #check to make sure the file the user is trying to delete is valid
    if filestoragedb.isValidFile(chatroom_uuid, file_uuid):
        filestoragedb.deleteFile(chatroom_uuid, file_uuid);
        os.remove('files/' + file_uuid);
    else:
        raise HTTPException(status_code=403, detail="File does not exist or does not belong to the user")
    return;

