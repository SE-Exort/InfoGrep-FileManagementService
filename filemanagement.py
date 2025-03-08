import psycopg2
import os

from InfoGrep_BackendSDK.infogrep_logger.logger import Logger

class filemanagement:
    def __init__(self):
        # init logger
        self.logger = Logger("FileManagementServiceLogger")

        # DB config
        db_port = "5432"
        db_host = os.environ.get("PGHOST", "localhost")
        db_user = os.environ.get("POSTGRES_USERNAME", "postgres")
        db_password = os.environ.get("POSTGRES_PASSWORD", "example")
        db_name = os.environ.get("PG_DATABASE_NAME", "postgres")

        keepalive_kwargs = {
            "keepalives": 1,
            "keepalives_idle": 30,
            "keepalives_interval": 5,
            "keepalives_count": 5,
        }

        if os.environ.get("PG_VERIFY_CERT") == "true":
            ca_cert_path = os.environ["PG_CA_CERT_PATH"]
            client_cert_path = os.environ["PG_TLS_CERT_PATH"]
            client_key_path = os.environ["PG_TLS_KEY_PATH"]
            self.con = psycopg2.connect(
                database=db_name, user=db_user, password=db_password,
                host=db_host, port=db_port,
                sslmode='verify-full',
                sslrootcert=ca_cert_path, 
                sslcert=client_cert_path, 
                sslkey=client_key_path, 
                **keepalive_kwargs
            )
            self.logger.info("SSL DB connection established")
        else:
            self.con = psycopg2.connect(database=db_name, user=db_user, password=db_password, host=db_host, port=db_port, **keepalive_kwargs)
            self.logger.info("DB connection established")
        
        self.cursor = self.con.cursor()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS filelists (\
                                FILEUUID CHAR(36) PRIMARY KEY,\
                                CHATROOM CHAR(36) NOT NULL,\
                                FILENAME VARCHAR NOT NULL,\
                                UPLOADUSER CHAR(36) NOT NULL,\
                                FILESIZE BIGINT NOT NULL)")
        
    def getFilesFromChatroom(self, chatroom_uuid):
        self.cursor.execute("SELECT FILEUUID, FILENAME FROM filelists WHERE CHATROOM = %s", (str(chatroom_uuid),))
        return self.cursor.fetchall()

    def createFile(self, user_id, chatroom_uuid, file_uuid, file_name, file_size):
        self.cursor.execute("INSERT INTO filelists(FILEUUID,CHATROOM,FILENAME,UPLOADUSER,FILESIZE) VALUES(%s,%s,%s,%s,%s)", (str(file_uuid),str(chatroom_uuid),str(file_name),str(user_id),file_size))
        self.con.commit()
    
    def deleteFile(self, chatroom_uuid, file_uuid):
        self.cursor.execute("DELETE FROM filelists WHERE CHATROOM = %s AND FILEUUID = %s", (str(chatroom_uuid), str(file_uuid)))
        self.con.commit()

    def isValidFile(self, chatroom_uuid, file_uuid):
        self.cursor.execute("SELECT * FROM filelists WHERE CHATROOM = %s AND FILEUUID = %s", (str(chatroom_uuid), str(file_uuid)))
        fileexists = self.cursor.fetchall()
        if not fileexists:
            return 0
        return 1

    def getFileName(self, chatroom_uuid, file_uuid):
        self.cursor.execute("SELECT FILENAME FROM filelists WHERE CHATROOM = %s AND FILEUUID = %s", (str(chatroom_uuid), str(file_uuid)))
        matchingfiles = self.cursor.fetchone()
        return matchingfiles[0]

    def adminGetAllFiles(self):
        self.cursor.execute("SELECT FILEUUID, CHATROOM, UPLOADUSER, FILENAME, FILESIZE FROM filelists")
        return self.cursor.fetchall()

    def adminDeleteFile(self, file_uuid):
        self.cursor.execute("DELETE FROM filelists WHERE FILEUUID = %s", (str(file_uuid),))
        self.con.commit()

    def adminIsValidFile(self, file_uuid):
        self.cursor.execute("SELECT * FROM filelists WHERE FILEUUID = %s", (str(file_uuid),))
        fileexists = self.cursor.fetchall()
        if not fileexists:
            return 0
        return 1
