import os
import time
import logging
import requests
import schedule
import psycopg2
from datetime import datetime, timezone
from psycopg2.extras import execute_values

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(message)s")

GBFS_DISCOVERY_URL = os.environ["GBFS_BASE_URL"]   # now the gbfs.json discovery URL
INTERVAL = int(os.environ.get("FETCH_INTERVAL_MINUTES", "5"))

DB_DSN = (
    f"host={os.environ['POSTGRES_HOST']} "
    f"port={os.environ.get('POSTGRES_PORT', '5432')} "
    f"dbname={os.environ['POSTGRES_DB']} "
    f"user={os.environ['POSTGRES_USER']} "
    f"password={os.environ['POSTGRES_PASSWORD']}"
)

HEALTH_FILE = "/tmp/healthy"


def fetch_json(url: str) -> dict:
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    return r.json()


def resolve_feed_urls() -> dict:
    """Read the GBFS discovery doc and return {feed_name: url}."""
    disc = fetch_json(GBFS_DISCOVERY_URL)
    data = disc["data"]
    # Discovery is keyed by language; prefer 'en', else first available.
    lang = "en" if "en" in data else next(iter(data))
    feeds = data[lang]["feeds"]
    return {f["name"]: f["url"] for f in feeds}


def upsert_stations(conn, stations: list):
    sql = """
        INSERT INTO stations(station_id, name, lat, lon, capacity)
        VALUES %s
        ON CONFLICT (station_id) DO UPDATE
          SET name=EXCLUDED.name, lat=EXCLUDED.lat,
              lon=EXCLUDED.lon, capacity=EXCLUDED.capacity
    """
    rows = [(s["station_id"], s["name"], s["lat"], s["lon"], s.get("capacity", 0))
            for s in stations]
    with conn.cursor() as cur:
        execute_values(cur, sql, rows)
    conn.commit()


def insert_snapshots(conn, statuses: list, fetched_at: datetime):
    sql = """
        INSERT INTO station_snapshots
          (station_id, fetched_at, num_bikes_avail, num_docks_avail, is_renting, is_returning)
        VALUES %s
    """
    rows = [
        (
            s["station_id"],
            fetched_at,
            s.get("num_bikes_available", 0),
            s.get("num_docks_available", 0),
            bool(s.get("is_renting", 0)),
            bool(s.get("is_returning", 0)),
        )
        for s in statuses
    ]
    with conn.cursor() as cur:
        execute_values(cur, sql, rows)
    conn.commit()


def mark_healthy():
    with open(HEALTH_FILE, "w") as f:
        f.write(datetime.now(timezone.utc).isoformat())


def run():
    logging.info("Fetching BIXI data...")
    fetched_at = datetime.now(timezone.utc)
    try:
        feeds = resolve_feed_urls()
        info_data   = fetch_json(feeds["station_information"])
        status_data = fetch_json(feeds["station_status"])

        with psycopg2.connect(DB_DSN) as conn:
            upsert_stations(conn, info_data["data"]["stations"])
            insert_snapshots(conn, status_data["data"]["stations"], fetched_at)

        n = len(status_data["data"]["stations"])
        logging.info(f"Inserted {n} snapshots")
        mark_healthy()
    except Exception as e:
        logging.error(f"Fetch failed: {e}")


if __name__ == "__main__":
    run()
    schedule.every(INTERVAL).minutes.do(run)
    while True:
        schedule.run_pending()
        time.sleep(30)