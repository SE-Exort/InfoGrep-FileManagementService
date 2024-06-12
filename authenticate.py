from fastapi import HTTPException

#apis used to authenticate if a user should be allowed to do some action

def auth_user(user_id, cookie):
    #check to see if the user and their session cookie are valid
    if not cookie == 'a':
        raise HTTPException(status_code=401, detail="User or session cookie invalid")
    return;

def auth_user_chatroom(user_id, chatroom_id):
    #check to see if a user should be allowed to access a chatroom
    if not user_id == chatroom_id:
        raise HTTPException(status_code=403, detail="User not in chatroom")
    return;