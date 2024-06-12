import json;
import uuid;
import os;
from fastapi import FastAPI;
from fastapi import UploadFile;
from fastapi.responses import FileResponse

from authenticate import *;
import filemanagement;

filemanagementservice = FastAPI();
filestoragedb = filemanagement.filemanagement();

@filemanagementservice.get('/filelist')
def get_filelist(chatroom_id, user_id, cookie):
    #authenticate user and chatroom
    #user must have a valid session cookie
    auth_user(user_id=user_id, cookie=cookie)
    auth_user_chatroom(user_id=user_id, chatroom_id=chatroom_id);

    #obtain the list of files in the specified chatroom as well as the file uuids
    filelist = filestoragedb.getFilesFromUserandChatroom(user_id=user_id,chatroom_id=chatroom_id);
    return filelist;

@filemanagementservice.get('/file')
def get_file(chatroom_id, user_id, file_id, cookie):
    #authenticate user and chatroom
    #user must have a valid session cookie
    auth_user(user_id=user_id, cookie=cookie)
    auth_user_chatroom(user_id=user_id, chatroom_id=chatroom_id);

    #verify if file exists for user_id and chatroom_id
    if filestoragedb.isValidFile(user_id, chatroom_id, file_id):
        return FileResponse(path='files/' + file_id, filename=filestoragedb.getFileName(user_id, chatroom_id, file_id));
    raise HTTPException(status_code=403, detail="Requested file not found");

@filemanagementservice.post('/file')
async def post_file(chatroom_id, user_id, cookie, uploadedfile: UploadFile):
    #authenticate user and chatroom
    #user must have a valid session cookie
    auth_user(user_id=user_id, cookie=cookie)
    auth_user_chatroom(user_id=user_id, chatroom_id=chatroom_id);
    if uploadedfile.size > 10*1024*1024:
        raise HTTPException(status_code=403, detail="File too large")
    #upload the file from the user into the chatroom
    file_uuid = uuid.uuid4();

    with open('files/' + str(file_uuid), "wb") as file:
        content = await uploadedfile.read()  # async read chunk
        file.write(content)  # async write chunk
    
    
    filestoragedb.createFile(user_id, chatroom_id, file_uuid, uploadedfile.filename);
    return file_uuid;

@filemanagementservice.delete('/file')
def delete_file(chatroom_id, user_id, cookie, file_id):
    #authenticate user and chatroom
    #user must have a valid session cookie
    auth_user(user_id=user_id, cookie=cookie)
    auth_user_chatroom(user_id=user_id, chatroom_id=chatroom_id);
    #check to make sure the file the user is trying to delete is valid
    if filestoragedb.isValidFile(user_id, chatroom_id, file_id):
        filestoragedb.deleteFile(file_id);
        os.remove('files/' + file_id);
    else:
        raise HTTPException(status_code=403, detail="File does not exist or does not belong to the user")
    return;

