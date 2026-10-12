import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import osmnx as ox


load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL")
PLACE = "Chengdu, China"
NETWORK_TYPE = "drive"
NODES_TABLE = "osm_nodes"
EDGES_TABLE = "osm_edges"

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL must be set")

ox.settings.log_console = True

engine = create_engine(DATABASE_URL)

with engine.begin() as connection:
    connection.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))

print(f"Downloading {NETWORK_TYPE} network for {PLACE}...")
graph = ox.graph.graph_from_place(PLACE, network_type=NETWORK_TYPE)
nodes, edges = ox.convert.graph_to_gdfs(graph)

print(f"Writing {len(nodes)} nodes to {NODES_TABLE}...")
nodes.to_postgis(NODES_TABLE, engine, if_exists="replace")

print(f"Writing {len(edges)} edges to {EDGES_TABLE}...")
edges.to_postgis(EDGES_TABLE, engine, if_exists="replace")

print("OSM data loaded successfully.")
