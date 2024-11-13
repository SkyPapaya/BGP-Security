import mysql.connector
import datetime

class SQLHandler:
    '''
    generate MYSQL Entity
    '''
    def __init__(self) -> None:
        self.sqlhandler = mysql.connector.connect(user="minio", password="Cnic2022_",
                            host="192.168.1.14",
                            database="minio",
                            port=3309,
                            buffered=True)
    
    def getFileFromSQL(self,query:str) -> list:
        assert(self.sqlhandler!=None)
        cursor = self.sqlhandler.cursor()
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()
        res = []
        for (File,) in data:
            res.append(File)
        return res

    def checkFileExist(self,tablename:str,filename:str) -> bool:
        res = True
        cursor = self.sqlhandler.cursor()
        query = "SELECT 1 FROM %s WHERE File = '%s' limit 1"%(tablename,filename)
        cursor.execute(query)
        data = cursor.fetchall()
        if len(data) == 0:
            res = False
        return res
    
    def closeSQL(self):
        self.sqlhandler.close()
    
if __name__=="__main__":
    sqlHandler = SQLHandler()
    print(sqlHandler.checkFileExist("bgpdataindex","rrc00_updates.20230301.1005.gz"))
    # start = datetime.datetime(2023,3,1,0,0)
    # end = datetime.datetime(2023,3,10,0,0)
    # stime=start.strftime("%Y-%m-%d %H:%M:%S")
    # etime=end.strftime("%Y-%m-%d %H:%M:%S")
    # query = "SELECT File FROM bgpdataindex WHERE Type = 'bview' AND Collector = 'rrc00' AND Time BETWEEN '%s' AND '%s'"%(stime,etime)
    # res = sqlHandler.getFileFromSQL(query)
    # for err in res:
    #     print(err)