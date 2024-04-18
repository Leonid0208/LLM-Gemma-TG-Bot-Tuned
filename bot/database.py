import os
import psycopg2
from time import sleep
from psycopg2 import sql
from datetime import datetime


class Handler:
    def __init__(self):
        print(os.environ)
        self.conn = psycopg2.connect(dbname=os.getenv("DB_dbname"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"))
        self.cursor = self.conn.cursor()
        self.CreateRequestsTable()
            

    def __del__(self):
        self.conn.close()

    def CreateRequestsTable(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS logs (
            id SERIAL PRIMARY KEY,
            request_date TIMESTAMP,
            response_date TIMESTAMP,
            question TEXT,
            answer TEXT,
            user_login VARCHAR(255),
            chat_id BIGINT
            );''')

    def insert(self, request_date: datetime, question: str, answer: str, user_login: str, chat_id: int):
        self.cursor.execute(
        sql.SQL("""
            INSERT INTO logs (request_date, response_date, question, answer, user_login, chat_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """),
        (request_date, datetime.now(), question, answer, user_login, chat_id)
        )

    def flush(self):
        self.conn.commit()