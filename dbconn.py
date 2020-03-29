import pandas as pd
import psycopg2
import pypyodbc


class pgdb:
    conn = None

    def __init__(self):
        self.conn = psycopg2.connect(
            host="192.168.1.110",
            database="ALTERDATA_SHOP",
            user="postgres",
            password="123456",
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
