# XML → Redis exporter

Exports `config.xml` into Redis:

- `subdomains` → JSON array of all subdomains
- `cookie:<NAME>:<HOST>` → the cookie's value (e.g. `cookie:dlp-avast:amazon`)

## Requirements
- Docker Desktop must be running
- If you face permission issues, run `chmod +x export.sh`

## Run
  `./export.sh -v /path/to/config.xml`
(`-v` prints every key saved)

Example: `./export.sh -v config.xml`

## Unit tests
  `docker compose run --rm --build tests`

## Stop Redis once finished
  `docker compose down`

## NOTES
- Redis client is injected, so tests use memory instead and need no server
- All keys are written with one atomic `MSET`

### Contents
- `config.xml`          → given data
- `export.sh`           → command to run
- `docker-compose.yml`  → define redis and app containers
- `Dockerfile`          → describe app container
- `export_to_redis.py`  → program: read XML, build/save keys, handles command line & file path
- `test_export_to_redis.py` → checks that program works
- `requirements.txt`    → necessary Python library (redis)
