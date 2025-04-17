# nyctrains API

A FastAPI-based backend and Python package for working with the MTA's real-time subway and LIRR GTFS-RT data feeds. This project fetches, parses, and exposes real-time feeds as human-readable JSON, including stop names and (for LIRR) route names. You can use it as an HTTP API or as a Python library in your own projects.

## Features
- Proxies and parses the MTA GTFS-RT feeds for all major subway lines and LIRR
- Converts all Unix timestamps to ISO 8601 strings for easy reading
- Adds `stop_name` (from stops.txt or stops-lirr.txt) alongside every `stop_id`
- For LIRR, adds `route_long_name` (from routes-lirr.txt) alongside every `route_id`
- Unified endpoint: `/subway/{feed}/json` (see below for all supported feeds)
- Ready for extension to other lines or custom endpoints
- **Usable as a Python package:** import and use MTAClient or other utilities in your own code

## Supported Feeds
- `ace` (A, C, E)
- `bdfm` (B, D, F, M)
- `g` (G)
- `jz` (J, Z)
- `nqrw` (N, Q, R, W)
- `l` (L)
- `si` (Staten Island Railway)
- `1234567` (1, 2, 3, 4, 5, 6, 7, S)
- `lirr` (Long Island Rail Road)

## Quickstart (as an API)

### 1. Clone the repository
```bash
git clone https://github.com/arrismo/nyctrains.git
cd nyctrains
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
# or, if you want to use as a package:
pip install .
```

### 3. (No API key or .env file required)
You do **not** need an API key or a `.env` file to use this project. All feeds are public.

### 4. Run the FastAPI server
```bash
uvicorn nyctrains.main:app --reload
```

### 5. Access the API
- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- Example: [http://localhost:8000/subway/ace/json](http://localhost:8000/subway/ace/json)
- Example: [http://localhost:8000/subway/lirr/json](http://localhost:8000/subway/lirr/json)

## Usage as a Python Library
Install in your project:
```bash
pip install git+https://github.com/arrismo/nyctrains.git
```

Example usage:
```python
from nyctrains.mta_client import MTAClient
import asyncio

async def main():
    client = MTAClient()
    data = await client.get_gtfs_feed("nyct%2Fgtfs-ace")
    # process GTFS-RT data as needed

asyncio.run(main())
```

You can also import and use any utility functions/classes you expose in your package.

## Example Output
```json
{
  "header": {
    "gtfs_realtime_version": "2.0",
    "timestamp": "2025-04-15T21:04:02+00:00"
  },
  "entity": [
    {
      "id": "GO304_25_809_T",
      "trip_update": {
        "trip": {
          "trip_id": "GO304_25_809",
          "start_date": "20250415",
          "schedule_relationship": 0,
          "route_id": "6",
          "route_long_name": "Long Beach Branch",
          "direction_id": 1
        },
        "stop_time_update": [
          {
            "stop_id": "LBG",
            "stop_name": "Long Beach"
          }
        ]
      }
    }
  ]
}
```

## Data Resources
- All static mapping files are in the `resources/` directory:
  - `resources/stops.txt` (NYC Subway stops)
  - `resources/stops-lirr.txt` (LIRR stops)
  - `resources/routes-lirr.txt` (LIRR route names)

**Note:** If you deploy or share this repo, make sure these files are present on your server even if they are gitignored.

## Development
- All main code is in the `nyctrains/` package.
- See `main.py` for API endpoints and `mta_client.py` for MTA API access logic.
- Extend or customize endpoints as needed!