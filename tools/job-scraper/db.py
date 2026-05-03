import os
import sqlite3

DB_NAME = os.getenv("DB_PATH", "jobs.db")

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        company TEXT,
        link TEXT UNIQUE,
        score INTEGER,
        category TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()


def insert_job(job):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    try:
        c.execute("""
        INSERT INTO jobs (title, company, link, score, category)
        VALUES (?, ?, ?, ?, ?)
        """, (job["title"], job["company"], job["link"], job["score"], job["category"]))
        conn.commit()
    except:
        pass  # duplicate (ignore)

    conn.close()