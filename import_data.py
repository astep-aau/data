import ast
import csv
import io
import json
import os
import zipfile

import geopandas as gpd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text


ZIP_FILE = "bj_data.zip"
DATA_DIR = "bj_data"
TRAJECTORY_FILES = [
    "traj_train_20.csv",
    "traj_train_40.csv",
    "traj_train_60.csv",
    "traj_train_80.csv",
    "traj_train_100.csv",
    "traj_valid.csv",
    "traj_test.csv",
]


def unzip():
    if os.path.exists(DATA_DIR):
        return

    print("Unzipping data...")
    with zipfile.ZipFile(ZIP_FILE) as zip_file:
        zip_file.extractall(DATA_DIR)


def insert_nodes(engine):
    print("Inserting nodes...")
    nodes = gpd.read_file(f"{DATA_DIR}/map/nodes.shp")
    nodes.to_postgis("osm_nodes", engine, if_exists="replace", index=False)


def insert_edges(engine):
    print("Inserting edges...")
    edges = gpd.read_file(f"{DATA_DIR}/map/edges.shp")
    edges.to_postgis("osm_edges", engine, if_exists="replace", index=False)
    with engine.begin() as connection:
        connection.execute(text("CREATE INDEX osm_edges_fid_idx ON osm_edges (fid)"))


def insert_rows(cursor, query, rows):
    file = io.StringIO()
    csv.writer(file, lineterminator="\n").writerows(rows)
    file.seek(0)
    cursor.copy_expert(query, file)


def insert_trajectories(engine):
    print("Inserting trajectories...")
    connection = engine.raw_connection()
    cursor = connection.cursor()
    cursor.execute("DROP VIEW IF EXISTS trajectory_lines")
    cursor.execute("DROP TABLE IF EXISTS trajectories")
    cursor.execute(
        """
        CREATE TABLE trajectories (
            dataset text,
            taxi_id text,
            trajectory_id text,
            gps_points jsonb,
            road_points jsonb
        )
        """
    )

    trajectory_query = (
        "COPY trajectories (dataset, taxi_id, trajectory_id, gps_points, road_points) "
        "FROM STDIN WITH CSV"
    )

    for filename in TRAJECTORY_FILES:
        print(f"  {filename}")
        rows = []
        with open(f"{DATA_DIR}/{filename}", newline="") as file:
            for row in csv.reader(file):
                gps_points = ast.literal_eval(row[2])
                rows.append(
                    (
                        filename[:-4],
                        row[0],
                        row[1],
                        json.dumps(gps_points, separators=(",", ":")),
                        json.dumps(ast.literal_eval(row[3]), separators=(",", ":")),
                    )
                )
                if len(rows) == 5000:
                    insert_rows(cursor, trajectory_query, rows)
                    rows = []

        if rows:
            insert_rows(cursor, trajectory_query, rows)

    cursor.execute(
        "CREATE INDEX trajectories_trip_idx ON trajectories (dataset, taxi_id, trajectory_id)"
    )
    cursor.execute(
        """
        CREATE VIEW trajectory_lines AS
        SELECT
            t.dataset,
            t.taxi_id,
            t.trajectory_id,
            ST_SetSRID(ST_MakeLine(e.geometry ORDER BY p.ordinality), 4326)::geometry(LineString, 4326) AS geometry
        FROM trajectories t
        CROSS JOIN LATERAL jsonb_array_elements(t.road_points)
            WITH ORDINALITY AS p(value, ordinality)
        JOIN osm_edges e
            ON e.fid = (p.value->>0)::bigint
        GROUP BY
            t.dataset,
            t.taxi_id,
            t.trajectory_id
        """
    )

    connection.commit()
    connection.close()


def main():
    load_dotenv()
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL must be set")

    unzip()
    engine = create_engine(database_url)
    with engine.begin() as connection:
        connection.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))

    insert_nodes(engine)
    insert_edges(engine)
    insert_trajectories(engine)
    print("Done")


if __name__ == "__main__":
    main()
