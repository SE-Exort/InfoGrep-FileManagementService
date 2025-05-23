import psycopg2
import os

from InfoGrep_BackendSDK.infogrep_logger.logger import Logger

class filemanagement:
    def __init__(self):
        # init logger
        self.logger = Logger("FileManagementServiceLogger")
        self.initDbConnection()
        self.cursor = self.con.cursor()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS filelists (\
                                FILEUUID CHAR(36) PRIMARY KEY,\
                                CHATROOM CHAR(36) NOT NULL,\
                                FILENAME VARCHAR NOT NULL,\
                                UPLOADUSER CHAR(36) NOT NULL,\
                                FILESIZE BIGINT NOT NULL)")
        
        self.cursor.execute("CREATE TABLE IF NOT EXISTS filebackend (\
                            FILEUUID CHAR(36) PRIMARY KEY,\
                            FILEOID INT NOT NULL\
                            )")
        self.cursor.close();
    
    def initDbConnection(self):
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
        self.con.autocommit = False;

    def getConnection(self):

        def try_cursor():
            cursor = self.con.cursor()
            cursor.execute('SELECT 1')
            cursor.close()
        
        try:
            try_cursor()
            return self.con
        except Exception:
            self.logger.warning("Pyscopg2 connection closed, re-establishing ...")
            self.initDbConnection()
            try_cursor()
            return self.con
        
    def getFilesFromChatroom(self, chatroom_uuid):
        connection = self.getConnection()
        cursor = connection.cursor();
        cursor.execute("SELECT FILEUUID, FILENAME FROM filelists WHERE CHATROOM = %s", (str(chatroom_uuid),))
        result = cursor.fetchall();
        cursor.close();
        return result;

    def createFile(self, user_id, chatroom_uuid, file_uuid, file_name, file_size):
        connection = self.getConnection()
        cursor = connection.cursor();
        cursor.execute("INSERT INTO filelists(FILEUUID,CHATROOM,FILENAME,UPLOADUSER,FILESIZE) VALUES(%s,%s,%s,%s,%s)", (str(file_uuid),str(chatroom_uuid),str(file_name),str(user_id),file_size))
        connection.commit()
        cursor.close();
    
    def deleteFile(self, chatroom_uuid, file_uuid):
        connection = self.getConnection()
        cursor = connection.cursor();
        cursor.execute("DELETE FROM filelists WHERE CHATROOM = %s AND FILEUUID = %s", (str(chatroom_uuid), str(file_uuid)))
        connection.commit()
        cursor.close();

    def isValidFile(self, chatroom_uuid, file_uuid):
        connection = self.getConnection()
        cursor = connection.cursor();
        cursor.execute("SELECT * FROM filelists WHERE CHATROOM = %s AND FILEUUID = %s", (str(chatroom_uuid), str(file_uuid)))
        fileexists = cursor.fetchall()
        cursor.close();
        if not fileexists:
            return 0
        return 1

    def getFileName(self, chatroom_uuid, file_uuid):
        connection = self.getConnection()
        cursor = connection.cursor();
        cursor.execute("SELECT FILENAME FROM filelists WHERE CHATROOM = %s AND FILEUUID = %s", (str(chatroom_uuid), str(file_uuid)))
        matchingfiles = cursor.fetchone()
        cursor.close();
        return matchingfiles[0]

    def adminGetAllFiles(self):
        connection = self.getConnection()
        cursor = connection.cursor();
        cursor.execute("SELECT FILEUUID, CHATROOM, UPLOADUSER, FILENAME, FILESIZE FROM filelists")
        result =  cursor.fetchall()
        cursor.close();
        return result;

    def adminDeleteFile(self, file_uuid):
        connection = self.getConnection()
        cursor = connection.cursor();
        cursor.execute("DELETE FROM filelists WHERE FILEUUID = %s", (str(file_uuid),))
        connection.commit()
        cursor.close();

    def adminIsValidFile(self, file_uuid):
        connection = self.getConnection()
        cursor = connection.cursor();
        cursor.execute("SELECT * FROM filelists WHERE FILEUUID = %s", (str(file_uuid),))
        fileexists = cursor.fetchall()
        cursor.close();
        if not fileexists:
            return 0
        return 1

    def backendSaveFile(self, file_uuid, file):
        connection = self.getConnection()
        write_object = connection.lobject(0, 'w');
        write_object.write(file)
        connection.commit()
        cursor = connection.cursor();
        cursor.execute("INSERT INTO filebackend(FILEUUID,FILEOID) VALUES(%s,%s)", (str(file_uuid),str(write_object.oid),))
        connection.commit()
        cursor.close();
        return
    
    def backendReadFile(self, file_uuid):
        connection = self.getConnection()
        cursor = connection.cursor();
        cursor.execute("SELECT FILEOID FROM filebackend WHERE FILEUUID = %s", (str(file_uuid),));
        file_oid = cursor.fetchone()[0]
        result = connection.lobject(file_oid, 'b');
        cursor.close();
        return result

    def backendDeleteFile(self, file_uuid):
        #delete the actual file
        connection = self.getConnection()
        cursor = connection.cursor();
        cursor.execute("SELECT FILEOID FROM filebackend WHERE FILEUUID = %s", (str(file_uuid),));
        file_oid = cursor.fetchone()[0]
        file = connection.lobject(file_oid, 'r');
        file.unlink();
        connection.commit();

        #delete the reference to the file
        cursor.execute("DELETE FROM filebackend WHERE FILEUUID = %s", (str(file_uuid), ));
        connection.commit()
        cursor.close();
