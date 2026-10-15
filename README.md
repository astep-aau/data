# aSTEP Data!

## Env stuff

### Must do

```bash
cp .env.example .env
```

### Nice to do (mostly if you want nice syntax sugar)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt
```

## Setup

For now it is running in Docker.
Make sure you have the latest Docker version and compose plugin.
btw if you find Docker slow, i would suggest using a different runtime like Colima.
Also, we might modify these scripts, when this is deployed with Kubernetes (it's not right now).

### Wanna setup everything

This installs everything, sets up the database, unpacks `bj_data.zip`, and imports it into PostGIS.

```bash
docker compose up -d --build
```

### Just setup db?

```bash
docker compose up -d --build db
```

### Just get data?

```bash
docker compose up -d --build get-data
```

The importer creates `osm_nodes`, `osm_edges`, and `trajectories`, plus a `trajectory_lines` view. The trajectory table stores `taxi_id` from CSV column 1 and `trajectory_id` from CSV column 2. `trajectory_lines` creates one road-following PostGIS line per trip when queried. Use `dataset = 'traj_train_100'` when viewing the complete training data because the smaller training files overlap. The ZIP is mounted into the importer container and extracted into `bj_data/`.

### Wanna watch?

```bash
docker compose logs -f
```
