import pyodbc, os, pandas as pd
from dotenv import load_dotenv


load_dotenv()

_db = os.getenv("DB_NAME")
_sever = os.getenv("DB_SERVER")
_user = os.getenv("DB_USER")
_password = os.getenv("DB_PASSWORD")

class DB:
    def __init__(self):
        self.connect()

    def connect(self):
        try:
            self.cnx = pyodbc.connect(
                "Driver={ODBC Driver 17 for SQL SERVER};"
                "Server="+_sever+";"
                "Database="+_db+";"
                "UID="+_user+";"
                "PWD="+_password+";"
            )
            self.exception = None
        except Exception as e:
            self.cnx = None
            self.exception = e

    def select(self,sql):
        try:
            if self.cnx is None:
                self.connect()
                return self.exception
            data = pd.read_sql(sql, self.cnx) 
        except Exception as e:
            self.connect()
            return e
        self.cnx.close
        return data

    def insert(self,data,tabla):
        columnas = str(tuple(data.columns)).replace("'","")
        valores = '( ?'
        for i in range(len(data.columns)-1):
            valores += ', ?'
        valores += ')'
        sql = "INSERT INTO {} {} VALUES {}".format(tabla,columnas,valores)
        registros = list(tuple(row) for row in data.values)

        try:    
            cur = self.cnx.cursor()
            cur.executemany(sql,registros )
            self.cnx.commit()
            cur.close
        except Exception as e:
            return e
        self.cnx.close
        return True

    def sql(self,sql):
        # Sentencia SQL
        return self.execute(sql) 

    def execute(self,sql):
        # Manejar error de ejecucion
        try:
            if self.cnx is None:
                self.connect()
                return self.exception
            cur = self.cnx.cursor()
            cur.execute(sql)
            self.cnx.commit()
            cur.close
            self.cnx.close
            return cur
        except Exception as e:
            self.connect()
            return e  