CREATE TABLE IF NOT EXISTS stations (
    station_id  TEXT PRIMARY KEY,
    name        TEXT,
    lat         DOUBLE PRECISION,
    lon         DOUBLE PRECISION,
    capacity    INT,
    inserted_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS station_snapshots (
    id              BIGSERIAL PRIMARY KEY,
    station_id      TEXT REFERENCES stations(station_id),
    fetched_at      TIMESTAMPTZ NOT NULL,
    num_bikes_avail INT,
    num_docks_avail INT,
    is_renting      BOOLEAN,
    is_returning    BOOLEAN
);

CREATE INDEX IF NOT EXISTS idx_snapshots_station_time
    ON station_snapshots(station_id, fetched_at DESC);

CREATE MATERIALIZED VIEW IF NOT EXISTS station_hourly AS
SELECT
    station_id,
    date_trunc('hour', fetched_at) AS hour,
    AVG(num_bikes_avail)::NUMERIC(5,2) AS avg_bikes,
    AVG(num_docks_avail)::NUMERIC(5,2) AS avg_docks,
    COUNT(*) AS sample_count
FROM station_snapshots
GROUP BY station_id, date_trunc('hour', fetched_at);

CREATE UNIQUE INDEX IF NOT EXISTS idx_station_hourly
    ON station_hourly(station_id, hour);