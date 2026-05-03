from fastapi import FastAPI
import sqlite3

app = FastAPI()

@app.get("/jobs")
def get_jobs():
    #conn = sqlite3.connect("jobs.db")
    conn = sqlite3.connect("jobs.db", check_same_thread=False)
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