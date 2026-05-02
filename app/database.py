import sqlite3
import datetime
import os

def get_db_connection(app):
    conn = sqlite3.connect(app.config['DATABASE_PATH'])
    conn.row_factory = sqlite3.Row
    return conn

def init_db(app):
    with app.app_context():
        conn = get_db_connection(app)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS tech_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                category TEXT NOT NULL,
                date TEXT NOT NULL,
                extracted_text_length INTEGER NOT NULL
            )
        ''')
        conn.commit()
        conn.close()

def insert_tech_log(filename, category, extracted_text_length, app):
    conn = get_db_connection(app)
    current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute(
        'INSERT INTO tech_logs (filename, category, date, extracted_text_length) VALUES (?, ?, ?, ?)',
        (filename, category, current_date, extracted_text_length)
    )
    conn.commit()
    conn.close()

def get_tech_logs(app):
    conn = get_db_connection(app)
    logs = conn.execute('SELECT * FROM tech_logs ORDER BY id DESC').fetchall()
    conn.close()
    return [dict(ix) for ix in logs]
