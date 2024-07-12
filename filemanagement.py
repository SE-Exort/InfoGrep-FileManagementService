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
        
    def getFilesFromChatroom(self, chatroom_uuid):
        self.cursor.execute("SELECT FILEUUID, FILENAME FROM filelists WHERE CHATROOM = ?;", (str(chatroom_uuid),));
        return self.cursor.fetchall();

    def createFile(self, user_id, chatroom_uuid, file_uuid, file_name):
        self.cursor.execute("INSERT INTO filelists(FILEUUID,CHATROOM,FILENAME,UPLOADUSER) VALUES(?,?,?,?)", (str(file_uuid),str(chatroom_uuid),str(file_name),str(user_id)));
        self.con.commit();
    
    def deleteFile(self, chatroom_uuid, file_uuid):
        self.cursor.execute("DELETE FROM filelists WHERE CHATROOM = ? AND FILEUUID = ?", (str(chatroom_uuid), str(file_uuid)));
        self.con.commit();

    def isValidFile(self, chatroom_uuid, file_uuid):
        self.cursor.execute("SELECT * FROM filelists WHERE CHATROOM = ? AND FILEUUID = ?", (str(chatroom_uuid), str(file_uuid)));
        fileexists = self.cursor.fetchall();
        if not fileexists:
            return 0;
        return 1;

    def getFileName(self, chatroom_uuid, file_uuid):
        self.cursor.execute("SELECT FILENAME FROM filelists WHERE CHATROOM = ? AND FILEUUID = ?", (str(chatroom_uuid), str(file_uuid)));
        matchingfiles = self.cursor.fetchone();
        return matchingfiles[0];

