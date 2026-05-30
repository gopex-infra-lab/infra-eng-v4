import os
import psycopg

DATABASE_URL = os.getenv("DATABASE_URL")

def init_db():
    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                id SERIAL PRIMARY KEY,
                title TEXT,
                company TEXT,
                link TEXT UNIQUE,
                score INTEGER,
                category TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)

            conn.commit()


def insert_job(job):
    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            try:
                cur.execute("""
                INSERT INTO jobs (title, company, link, score, category)
                VALUES (%s, %s, %s, %s, %s)
                """, (job["title"], job["company"], job["link"], job["score"], job["category"]))
                conn.commit()
            except:
                pass  # duplicate (ignore)