import psycopg2
import os


class filemanagement:
    def __init__(self):
        # DB config
        db_port = "5432"
        db_host = os.environ.get("PGHOST", "file-management-service-postgres")
        db_user = os.environ.get("POSTGRES_USERNAME", "postgres")
        db_password = os.environ.get("POSTGRES_PASSWORD", "example")
        db_name = os.environ.get("PG_DATABASE_NAME", "postgres")
        DATABASE_URL = f"postgresql://{db_user}:{db_password}@{db_host}/{db_name}"

        keepalive_kwargs = {
            "keepalives": 1,
            "keepalives_idle": 30,
            "keepalives_interval": 5,
            "keepalives_count": 5,
        }

        self.con = psycopg2.connect(database=db_name, user=db_user, password=db_password, host=db_host, port=db_port, **keepalive_kwargs);
        self.cursor = self.con.cursor();
        self.cursor.execute("CREATE TABLE IF NOT EXISTS filelists (\
                                FILEUUID CHAR(37) PRIMARY KEY,\
                                CHATROOM CHAR(37) NOT NULL,\
                                FILENAME VARCHAR NOT NULL,\
                                UPLOADUSER CHAR(37) NOT NULL,\
                                FILESIZE BIGINT NOT NULL)")
        
    def getFilesFromChatroom(self, chatroom_uuid):
        self.cursor.execute("SELECT FILEUUID, FILENAME FROM filelists WHERE CHATROOM = %s", (str(chatroom_uuid),));
        return self.cursor.fetchall();

    def createFile(self, user_id, chatroom_uuid, file_uuid, file_name, file_size):
        self.cursor.execute("INSERT INTO filelists(FILEUUID,CHATROOM,FILENAME,UPLOADUSER,FILESIZE) VALUES(%s,%s,%s,%s,%s)", (str(file_uuid),str(chatroom_uuid),str(file_name),str(user_id),file_size));
        self.con.commit();
    
    def deleteFile(self, chatroom_uuid, file_uuid):
        self.cursor.execute("DELETE FROM filelists WHERE CHATROOM = %s AND FILEUUID = %s", (str(chatroom_uuid), str(file_uuid)));
        self.con.commit();

    def isValidFile(self, chatroom_uuid, file_uuid):
        self.cursor.execute("SELECT * FROM filelists WHERE CHATROOM = %s AND FILEUUID = %s", (str(chatroom_uuid), str(file_uuid)));
        fileexists = self.cursor.fetchall();
        if not fileexists:
            return 0;
        return 1;

    def getFileName(self, chatroom_uuid, file_uuid):
        self.cursor.execute("SELECT FILENAME FROM filelists WHERE CHATROOM = %s AND FILEUUID = %s", (str(chatroom_uuid), str(file_uuid)));
        matchingfiles = self.cursor.fetchone();
        return matchingfiles[0];

    def adminGetAllFiles(self):
        self.cursor.execute("SELECT FILEUUID, CHATROOM, UPLOADUSER, FILENAME, FILESIZE FROM filelists");
        return self.cursor.fetchall();

    def adminDeleteFile(self, file_uuid):
        self.cursor.execute("DELETE FROM filelists WHERE FILEUUID = %s", (str(file_uuid),));
        self.con.commit();

    def adminIsValidFile(self, file_uuid):
        self.cursor.execute("SELECT * FROM filelists WHERE FILEUUID = %s", (str(file_uuid),));
        fileexists = self.cursor.fetchall();
        if not fileexists:
            return 0;
        return 1;
