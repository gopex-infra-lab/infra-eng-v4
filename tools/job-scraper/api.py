from fastapi import FastAPI
import sqlite3
import os

DB_PATH = os.getenv("DB_PATH", "/data/jobs.db")

app = FastAPI()

@app.get("/jobs")
def get_jobs():
    #conn = sqlite3.connect("jobs.db")
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()

    c.execute("""
    SELECT title, company, link, score, category
    FROM jobs
    ORDER BY score DESC
    LIMIT 20
    """)

    rows = c.fetchall()
    conn.close()

    return [
        {
            "title": r[0],
            "company": r[1],
            "link": r[2],
            "score": r[3],
            "category": r[4]
        }
        for r in rows
    ]