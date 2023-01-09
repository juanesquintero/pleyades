import os
from functools import wraps
from dotenv import load_dotenv
import mysql.connector as mysql


import ssl
ctx = ssl.SSLContext()
ctx.minimum_version = ssl.TLSVersion.TLSv1_1


load_dotenv()

_user = os.getenv('MYSQL_USER')
_password = os.getenv('MYSQL_PASSWORD')
_database = os.getenv('MYSQL_DATABASE')


def validate_connection(f):
    @wraps(f)
    def decorated_function(self, *args, **kwargs):
        if not(self.cnx):
            self.connect()
            raise Exception('Conexión caida a la BD de PLEYADES!')
        else:
            try:
                return f(self, *args, **kwargs)
            except Exception as e:
                self.close_connection()
                self.connect()
                raise Exception('Conexión caida a la BD de PLEYADES!')
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
            self.cnx = mysql.MySQLConnection(
                host='db-host',
                port=3306,
                user=_user,
                password=_password,
                database=_database,
            )
        except Exception as e:
            print(e, flush=True)
            self.close_connection()

    def close_connection(self):
        if self.cnx:
            if self.cnx.is_connected():
                self.cnx.close()
        self.cnx = None

    def execute(self, sql):
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

    @validate_connection
    def insert(self, body, tabla):
        # Keys Body
        columns = str(tuple(body.keys())).replace("'", "`")
        # Values Body
        values = str(tuple(body.values()))
        # Sentencia SQL
        sql = "INSERT INTO {} {} VALUES{}".format(
            tabla, columns, values).replace('None', 'NULL')
        return self.execute(sql)

    @validate_connection
    def select(self, sql):
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
    def update(self, body, condicion, tabla):
        # Sentencia SQL
        set_values = '`'+str(body)[2:-1].replace("':", "`=").replace(", '", ", `")
        sql = "UPDATE {} SET {} WHERE {};".format(
            tabla, set_values, condicion).replace('None', 'NULL')
        return self.execute(sql)

    @validate_connection
    def delete(self, condicion, tabla):
        # Sentencia SQL
        sql = "DELETE FROM {} WHERE {};".format(tabla, condicion)
        return self.execute(sql)
