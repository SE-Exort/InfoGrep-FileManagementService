import uuid;

from fastapi import APIRouter, HTTPException, Request
from fastapi import UploadFile;
from fastapi.responses import FileResponse
from fastapi.openapi.docs import get_swagger_ui_html

from InfoGrep_BackendSDK.infogrep_logger.logger import Logger
from InfoGrep_BackendSDK.infogrep_struct.logger_struct import LoggerStruct
log = Logger("FileManagementServiceLogger")

from InfoGrep_BackendSDK import authentication_sdk, room_sdk, ai_sdk
import filemanagement;

from Backends.backend import Backend
from Backends.filesystem import FileSystem

filebackend : Backend;
filebackend = FileSystem("files/");

router = APIRouter(prefix='/api', tags=["api"]);
filestoragedb = filemanagement.filemanagement();

@router.get('/filelist')
def get_filelist(request: Request, chatroom_uuid, cookie):
    #authenticate user and chatroom
    #user must have a valid session cookie
    user = authentication_sdk.User(cookie, headers=request.headers)
    user_uuid = user.profile()['user_uuid'];
    room_sdk.get_userInRoom(chatroom_uuid=chatroom_uuid, cookie=cookie, headers=request.headers);

    #obtain the list of files in the specified chatroom as well as the file uuids
    filelist = filestoragedb.getFilesFromChatroom(chatroom_uuid=chatroom_uuid);
    filelistjson = {'list': []}
    for item in filelist:
        filelistjson['list'].append({'File_UUID': item[0], 'File_Name': item[1]})
    return filelistjson;

@router.head('/file')
@router.get('/file')
def get_file(request: Request, chatroom_uuid, file_uuid, cookie):
    #authenticate user and chatroom
    #user must have a valid session cookie
    user = authentication_sdk.User(cookie, headers=request.headers)
    user_uuid = user.profile()['user_uuid'];
    room_sdk.get_userInRoom(chatroom_uuid=chatroom_uuid, cookie=cookie, headers=request.headers);

    #verify if file exists for chatroom_uuid
    if filestoragedb.isValidFile(chatroom_uuid, file_uuid):
        return filebackend.get_file(file_uuid=file_uuid, file_name=filestoragedb.getFileName(chatroom_uuid, file_uuid));
    raise HTTPException(status_code=403, detail="Requested file not found");

@router.post('/file')
async def post_file(request: Request, chatroom_uuid, uploadedfile: UploadFile, cookie):
    #authenticate user and chatroom
    #user must have a valid session cookie
    user = authentication_sdk.User(cookie, headers=request.headers)
    user_uuid = user.profile()['user_uuid'];
    room_sdk.get_userInRoom(chatroom_uuid=chatroom_uuid, cookie=cookie, headers=request.headers);

    if uploadedfile.size > 10*1024*1024:
        raise HTTPException(status_code=403, detail="File too large")
    #upload the file from the user into the chatroom
    file_uuid = uuid.uuid4();

    await filebackend.save_file(str(file_uuid), uploadedfile=uploadedfile)
    
    #ai_sdk.parse_postStartParsing(chatroom_uuid=chatroom_uuid, file_uuid=file_uuid, filetype="PDF", cookie=cookie, headers=request.headers);
    
    filestoragedb.createFile(user_uuid, chatroom_uuid, file_uuid, uploadedfile.filename, uploadedfile.size);

    return file_uuid;

@router.delete('/file')
def delete_file(request: Request, chatroom_uuid, file_uuid, cookie):
    #authenticate user and chatroom
    #user must have a valid session cookie
    user = authentication_sdk.User(cookie, headers=request.headers)
    user_uuid = user.profile()['user_uuid'];
    room_sdk.get_userInRoom(chatroom_uuid=chatroom_uuid, cookie=cookie, headers=request.headers);

    #check to make sure the file the user is trying to delete is valid
    if filestoragedb.isValidFile(chatroom_uuid=chatroom_uuid, file_uuid=file_uuid):
        filestoragedb.deleteFile(chatroom_uuid=chatroom_uuid, file_uuid=file_uuid);
        filebackend.delete_file(file_uuid=file_uuid);
    else:
        raise HTTPException(status_code=403, detail="File does not exist or does not belong to the user")
    return;

@router.get('/admin-all-files')
def admin_get_all_files(request: Request, cookie):
    #authenticate user and chatroom
    #user must have a valid session cookie
    log_info = LoggerStruct(Endpoint='/admin-all-files', Cookie=cookie)

    log.info(msg="Message: Got Admin request to get all files", extra=log_info.model_dump())
    user = authentication_sdk.User(cookie, headers=request.headers)
    log_info.User_UUID = user.profile()['user_uuid']

    log.info(msg="Message: User exists", extra=log_info.model_dump())
    if not user.profile()['is_admin']:
        log.error(msg="User exists but is not admin", extra=log_info.model_dump())
        raise HTTPException(status_code=401, detail="User is not an admin")
    log.info(msg="User exists and is admin", extra=log_info.model_dump())

    filelist = filestoragedb.adminGetAllFiles();
    filelistjson = {'list': []}
    for item in filelist:
        filelistjson['list'].append({'File_UUID': item[0], 'Chatroom_UUID': item[1], 'Uploader_UUID': item[2], 'File_Name': item[3], 'File_Size': item[4]})
    log.info(msg="Successfully returning all files in Service", extra=log_info.model_dump())
    return filelistjson;

@router.delete('/admin-delete-file')
def admin_delete_file(request: Request, file_uuid, cookie):
    #authenticate user and chatroom
    #user must have a valid session cookie
    log_info = LoggerStruct(Endpoint='/admin-delete-file', Cookie=cookie, File_UUID=str(file_uuid))

    log.info(msg="Got Admin request to delete file", extra=log_info.model_dump());

    user = authentication_sdk.User(cookie, headers=request.headers)
    log_info.User_UUID = user.profile()['user_uuid']

    log.info(msg="User exists", extra=log_info.model_dump())
    if not user.profile()['is_admin']:
        log.error(msg="User exists but is not admin", extra=log_info.model_dump())
        raise HTTPException(status_code=401, detail="User is not an admin")
    log.info(msg="User exists and is admin", extra=log_info.model_dump());

    #check to make sure the file the user is trying to delete is valid
    if filestoragedb.adminIsValidFile(file_uuid=file_uuid):
        log.info(msg="File Exists", extra=log_info.model_dump());
        filestoragedb.adminDeleteFile(file_uuid=file_uuid);
        filebackend.delete_file(file_uuid=file_uuid);
        log.info(msg="Successfully deleted file from Service", extra=log_info.model_dump());
    else:
        log.error(msg="File Does not exist", extra=log_info.model_dump());
        raise HTTPException(status_code=403, detail="File does not exist or does not belong to the user")

@router.get("/docs")
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url="/fms/openapi.json",
        title="File Management API Doc"
    )