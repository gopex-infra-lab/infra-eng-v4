from fastapi import FastAPI
import os
import psycopg

DATABASE_URL = os.getenv("DATABASE_URL")

app = FastAPI()

@app.get("/jobs")
def get_jobs():
    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT title, company, link, score, category
                FROM jobs
                ORDER BY score DESC
                LIMIT 20
            """)

            rows = cur.fetchall()

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

    
@app.get("/health")
def health():
    return {"status": "Ok"}