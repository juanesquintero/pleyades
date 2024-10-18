import os
import pyodbc
import logging
from functools import wraps
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()
error_logger = logging.getLogger('error_logger')

_db = os.getenv('CLI_DB_NAME')
_host = os.getenv('CLI_DB_SERVER')
_user = os.getenv('CLI_DB_USER')
_password = os.getenv('CLI_DB_PASSWORD')

ies_name = os.getenv('CLI_IES_NAME')

str_conn = f'mssql+pyodbc://{_user}:{_password}@{_host}:1433/{
    _db}?driver=ODBC+Driver+17+for+SQL+SERVER&timeout=120'

conn_fail_msg = f'Conexión caída BD Institución!! (SQL Server - {ies_name})'

# _drivers = [d for d in pyodbc.drivers()]
# driver = _drivers[-1] if _drivers else 'SQL Server'


def log_error(e):
    error_logger.error(f'EXCEPTION: base de datos IES ({ies_name})... {e}')


def validate_connection(f):
    @wraps(f)
    def decorated_function(self, *args, **kwargs):
        if not self.cnx:
            self.connect()
            raise Exception(conn_fail_msg)

        try:
            return f(self, *args, **kwargs)
        except Exception as e:
            self.close_connection()
            log_error(e)
            self.connect()
            raise Exception(conn_fail_msg)

    return decorated_function


class DB:
    __instance = None

    @staticmethod
    def getInstance():
        if DB.__instance is None:
            DB()
        return DB.__instance

    def __init__(self):
        if DB.__instance is not None:
            raise Exception('Esta clase es un Singleton!')
        else:
            self.cnx = None
            self.connect()
            DB.__instance = self

    def connect(self):
        try:
            engine = create_engine(str_conn)
            self.cnx = engine.raw_connection()
        except Exception as e:
            log_error(e)
            self.close_connection()

    def close_connection(self):
        if self.cnx:
            self.cnx.close()
        self.cnx = None

    @validate_connection
    def select(self, sql):
        try:
            if self.cnx is None:
                self.connect()
                return None
            with self.cnx.cursor() as cur:
                cur.execute(sql)
                rows = cur.fetchall()
                columns = [i[0] for i in cur.description]
                lista = []
                for row in rows:
                    REGISTRO = dict(zip(columns, row))
                    json = dict(REGISTRO)
                    lista.append(json)
                return lista
        except Exception as e:
            log_error(e)
            self.connect()
            raise e

    @validate_connection
    def insert(self, body, tabla):
        # Keys Body
        columns = str(tuple(body.keys())).replace("'", "")
        # Values Body
        values = str((tuple(body.values())))
        # Sentencia SQL
        sql = "INSERT INTO {} {} VALUES{}".format(
            tabla, columns, values).replace('None', 'NULL')
        return self.execute(sql)

    @validate_connection
    def multi_insert(self, data, tabla):
        columnas = str(tuple(data.columns)).replace("'", "")
        valores = '( ?'
        for _ in range(len(data.columns)-1):
            valores += ', ?'
        valores += ')'
        sql = "INSERT INTO {} {} VALUES {}".format(tabla, columnas, valores)
        registros = list(tuple(row) for row in data.values)

        try:
            with self.cnx.cursor() as cur:
                cur.executemany(sql, registros)
            self.cnx.commit()
            return True
        except Exception as e:
            log_error(e)
            raise e

    def sql(self, sql):
        # Sentencia SQL
        return self.execute(sql)

    @validate_connection
    def update(self, body, condicion, tabla):
        set_values = str(body)[2:-1].replace("':", " =").replace(", '", ", ")
        sql = "UPDATE {} SET {} WHERE {};".format(
            tabla, set_values, condicion
        ).replace('None', 'NULL')
        return self.execute(sql)

    @validate_connection
    def post_delete(self, condicion, tabla):
        # Sentencia SQL
        sql = "DELETE FROM {} WHERE {};".format(tabla, condicion)
        return self.execute(sql)

    @validate_connection
    def execute(self, sql):
        try:
            if self.cnx is None:
                self.connect()
                return None
            with self.cnx.cursor() as cur:
                cur.execute(sql)
                self.cnx.commit()
                return cur
        except Exception as e:
            log_error(e)
            raise e
