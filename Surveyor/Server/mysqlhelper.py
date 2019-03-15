# -*- coding: utf-8 -*-

import time
import pymysql

PY_MYSQL_CONN_DICT = {
    'host': 'localhost',  # This database is in the same server as the web.
    'user': 'root',
    'password': 'songxudong',
    # 'database': 'fringerprints',
    'port': 3306,
    'charset': 'utf8'
}

class DbConnection:

    def __init__(self):
        self.__conn_dict = PY_MYSQL_CONN_DICT
        self.conn = None
        self.cursor = None

    def connect(self, cursor=pymysql.cursors.DictCursor,db=None):
        self.conn = pymysql.connect(**self.__conn_dict)
        if db:
            self.conn.select_db(db)
        self.cursor = self.conn.cursor(cursor=cursor)
        return self.cursor

    def close(self):
        self.conn.commit()
        self.cursor.close()
        self.conn.close()

class UserModel(DbConnection):
    def run_out(self,command):
        try:
            self.connect()
            self.cursor.execute(command)
            self.close()
            return self.cursor.fetchall()
        except Exception as e:
            print e
    def run(self,command,db=None):
        try:
            self.connect(db=db)
            self.cursor.execute(command)
            self.close()
            return self.cursor.fetchall()
        except Exception as e:
            print e

