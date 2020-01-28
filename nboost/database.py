import time
from typing import Optional
from sqlite3 import Cursor
import sqlite3
from nboost import defaults


class Database:
    def __init__(self, db_file: type(defaults.db_file) = defaults.db_file, **_):
        self.db_file = db_file

    def new_row(self):
        return DatabaseRow()

    def get_cursor(self) -> Cursor:
        conn = sqlite3.connect(str(self.db_file), isolation_level=None)
        return conn.cursor()

    def insert(self, db_row: 'DatabaseRow'):
        cursor = self.get_cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS searches (
                time REAL,
                topk INTEGER,
                choices INTEGER,
                qa_time REAL,
                model_mrr REAL,
                server_mrr REAL,
                rerank_time REAL,
                response_time REAL
            );
        ''')

        cursor.execute('''            
            INSERT INTO searches (
                time,
                topk,
                choices,
                qa_time,
                model_mrr,
                server_mrr,
                rerank_time,
                response_time
            )
            VALUES(?,?,?,?,?,?,?,?);
        ''', (
            time.time(),
            db_row.topk,
            db_row.choices,
            db_row.qa_time,
            db_row.model_mrr,
            db_row.server_mrr,
            db_row.rerank_time,
            db_row.response_time
        ))

    def get_stats(self) -> dict:
        cursor = self.get_cursor()
        stats = cursor.execute('''
            SELECT
                AVG(topk) AS avg_topk,
                AVG(choices) AS avg_num_choices,
                AVG(rerank_time) AS avg_rerank_time,
                AVG(response_time) AS avg_response_time
            FROM searches
        ''').fetchone()
        columns = [column[0] for column in cursor.description]
        return dict(zip(columns, stats))


class DatabaseRow:
    def __init__(self):
        self.topk = None  # type: Optional[int]
        self.choices = None  # type: Optional[int]
        self.qa_time = None  # type: Optional[float]
        self.model_mrr = None  # type: Optional[float]
        self.server_mrr = None  # type: Optional[float]
        self.rerank_time = None  # type: Optional[float]
        self.response_time = None  # type: Optional[float]

