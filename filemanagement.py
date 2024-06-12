import sqlite3

class filemanagement:
    def __init__(self):
        self.con = sqlite3.connect("files/filedb.db", check_same_thread=False);
        self.cursor = self.con.cursor();
        self.cursor.execute("CREATE TABLE IF NOT EXISTS filelists (\
                                FILEUUID CHAR(37) PRIMARY KEY,\
                                CHATROOM CHAR(37) NOT NULL,\
                                FILENAME VARCHAR NOT NULL,\
                                UPLOADUSER CHAR(37) NOT NULL)")
        
    def getFilesFromUserandChatroom(self, user_id, chatroom_id):
        self.cursor.execute("SELECT FILEUUID, FILENAME FROM filelists WHERE UPLOADUSER = ? AND CHATROOM = ?;", (user_id, chatroom_id));
        return self.cursor.fetchall();

    def createFile(self, user_id, chatroom_id, file_uuid, file_name):
        self.cursor.execute("INSERT INTO filelists(FILEUUID,CHATROOM,FILENAME,UPLOADUSER) VALUES(?,?,?,?)", (str(file_uuid),chatroom_id,file_name,user_id));
        self.con.commit();
    
    def deleteFile(self, file_uuid):
        self.cursor.execute("DELETE FROM filelists WHERE FILEUUID = ?", (str(file_uuid),));
        self.con.commit();

    def isValidFile(self, user_id, chatroom_id, file_id):
        self.cursor.execute("SELECT * FROM filelists WHERE UPLOADUSER = ? AND CHATROOM = ? AND FILEUUID = ?", (str(user_id), str(chatroom_id), str(file_id)));
        fileexists = self.cursor.fetchall();
        if not fileexists:
            return 0;
        return 1;

    def getFileName(self, user_id, chatroom_id, file_id):
        self.cursor.execute("SELECT FILENAME FROM filelists WHERE UPLOADUSER = ? AND CHATROOM = ? AND FILEUUID = ?", (str(user_id), str(chatroom_id), str(file_id)));
        matchingfiles = self.cursor.fetchone();
        return matchingfiles[0];

