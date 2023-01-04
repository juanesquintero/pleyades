import os
import pyodbc
from functools import wraps
from dotenv import load_dotenv

load_dotenv()

_db = os.getenv("CLI_DB_NAME")
_host = os.getenv("CLI_DB_SERVER")
_user = os.getenv("CLI_DB_USER")
_password = os.getenv("CLI_DB_PASSWORD")

def validate_connection(f):
    @wraps(f)
    def decorated_function(self,*args, **kwargs):
        if not(self.cnx):
            self.connect()
            raise Exception('Conexión caida a la BD de la Institución!')
        else:
            try:
                return f(self, *args, **kwargs)
            except:
                self.close_connection()
                self.connect()
                raise Exception('Conexión caida a la BD de la Institución!')
    return decorated_function
class DB:
    __instance = None
    
    @staticmethod
    def getInstance():
        if DB.__instance == None:
            DB()
        return DB.__instance
    
    def __init__(self):
        if DB.__instance != None:
            raise Exception('Esta clase es un Singleton!')
        else:
            self.cnx = None
            self.connect()          
            DB.__instance = self

    def connect(self):
        try:
            self.cnx = pyodbc.connect(
                "Driver={ODBC Driver 17 for SQL SERVER};"
                "Server="+_host+";"
                "Database="+_db+";"
                "UID="+_user+";"
                "PWD="+_password+";"
            )
        except Exception as e:
            self.close_connection()
    
    def close_connection(self):
        if self.cnx:
            if self.cnx.is_connected():
                cnx.close()
        self.cnx = None
    
    @validate_connection
    def select(self,sql):
        try:
            if self.cnx is None:
                self.connect()
                return self.exception
            cur = self.cnx.cursor()
            cur.execute(sql)
        except Exception as e:
            self.connect()
            return e  

        lista = []
        rows = cur.fetchall()
        columns = [i[0] for i in cur.description]
        for row in rows:
            # Create a zip object from two lists
            REGISTRO = dict(zip(columns, row))
            # Create a dictionary from zip object
            json = dict(REGISTRO)
            lista.append(json)
        cur.close
        self.cnx.close
        return lista
    
    @validate_connection
    def insert(self,body,tabla):
        # Keys Body
        columns = str(tuple(body.keys())).replace("'", "")
        # Values Body
        values = str((tuple(body.values())))
        # Sentencia SQL
        sql = "INSERT INTO {} {} VALUES{}".format(tabla, columns, values).replace('None','NULL')
        return self.execute(sql)
    
    @validate_connection
    def multi_insert(self,data,tabla):
        columnas = str(tuple(data.columns)).replace("'","")
        valores = '( ?'
        for _ in range(len(data.columns)-1):
            valores += ', ?'
        valores += ')'
        sql = "INSERT INTO {} {} VALUES {}".format(tabla,columnas,valores)
        registros = list(tuple(row) for row in data.values)

        try:    
            cur = self.cnx.cursor()
            cur.executemany(sql, registros)
            cur.close
            self.cnx.commit()
        except Exception as e:
            return e
        self.cnx.close
        return True

    def sql(self,sql):
        # Sentencia SQL
        return self.execute(sql) 

    
    @validate_connection
    def update(self,body,condicion,tabla):
        set_values = str(body)[2:-1].replace("':"," =").replace(", '",", ")
        sql = "UPDATE {} SET {} WHERE {};".format(tabla, set_values, condicion).replace('None','NULL')
        return self.execute(sql) 
    
    @validate_connection
    def delete(self,condicion,tabla):
        # Sentencia SQL
        sql = "DELETE FROM {} WHERE {};".format(tabla, condicion)
        return self.execute(sql)
    
    @validate_connection
    def execute(self,sql):
        # Manejar error de ejecución
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

