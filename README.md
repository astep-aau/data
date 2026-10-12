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

This installs everything, sets up the database, and runs the get-data script.

```bash
docker compose up -d --build
```

### Just setup db?

```bash
docker compose up -d --build db
```

### Just get data?

Overpass API is kinda unstable, and im too lazy to setup retries, so just run it again if it fails (btw there is no need for --build if you need to rerun).

```bash
docker compose up -d --build get-data
```

You might wanna check:
https://downforeveryoneorjustme.com/overpass-api.de
https://overpass-api.de/api/status

### Wanna watch?

```bash
docker compose logs -f
```
