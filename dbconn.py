import pandas as pd
import psycopg2
import pypyodbc

host = ""
database = ""
user = ""
password = ""


class pgdb:
    conn = None

    def __init__(self):
        self.conn = psycopg2.connect(
            host=host.strip(), database=database, user=user, password=password,
        )

    def query(self, sql):
        return pd.read_sql(sql, con=self.conn)

    def execute(self, sql):
        cur = self.conn.cursor()
        cur.execute(sql)
        self.conn.commit()

    def close(self):
        self.conn.close()


class sqldb:
    conn = None

    def __init__(self):
        self.conn = pypyodbc.connect(
            "Driver={SQL Server};"
            "Server=192.168.1.5;"
            "Database=GwNetProducao;"
            "uid=sa;pwd=sysadm"
        )

    def query(self, sql):
        return pd.read_sql(sql, con=self.conn)

    def execute(self, sql):
        cur = self.conn.cursor()
        cur.execute(sql)

    def close(self):
        self.conn.close()
