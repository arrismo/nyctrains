# nyctrains API
[![Python Versions](https://img.shields.io/pypi/pyversions/nyctrains.svg)](https://pypi.python.org/pypi/nyctrains)
[![PyPI](https://img.shields.io/pypi/v/nyctrains)](https://pypi.org/project/nyctrains/#history)
[![PyPI Downloads](https://img.shields.io/pypi/dm/nyctrains)](https://pypistats.org/packages/nyctrains)
[![Repo Status](https://www.repostatus.org/badges/latest/active.svg)](https://www.repostatus.org/#active)
[![codecov](https://codecov.io/gh/arrismo/nyctrains/graph/badge.svg?token=AGXZZYUQU3)](https://codecov.io/gh/arrismo/nyctrains)
[![CI Build](https://github.com/arrismo/nyctrains/actions/workflows/ci-tests.yaml/badge.svg)](https://github.com/arrismo/nyctrains/actions/workflows/ci-tests.yaml)

A FastAPI-based backend and Python package for working with the MTA's real-time subway and LIRR GTFS-RT data feeds. This project fetches, parses, and exposes real-time feeds as human-readable JSON, including stop names and (for LIRR) route names. You can use it as an HTTP API or as a Python library in your own projects.

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

## Installation

Install using pip:

```sh
pip install nyctrains
```

## Static GTFS Data

This package relies on static GTFS data files being present in the `resources/` directory for full functionality (e.g., adding stop names, route details).

Required files:
- `resources/stops.txt` (NYC Subway + LIRR stops)
- `resources/routes.txt` (NYC Subway + LIRR routes)
- `resources/trips.txt`
- `resources/stop_times.txt`

*Note: The simple mappings for LIRR stop names (`stops-lirr.txt`) and route names (`routes-lirr.txt`) used in earlier versions have been replaced by the requirement for the full static GTFS files.* You can typically download these files from the MTA developer resources page.

The application loads these files into pandas DataFrames at startup using the `nyctrains.static_gtfs` module.

## Usage

This package provides Python tools and a FastAPI backend for working with MTA GTFS-RT subway and LIRR data. **No API key is required** to use the package or access the feeds.

### Running the API Server

```sh
# Make sure you have the static GTFS files in ./resources/
uvicorn nyctrains.main:app --reload
```

Access the API documentation at `http://127.0.0.1:8000/docs`.

Make requests to the feed endpoint, e.g.:
`http://127.0.0.1:8000/subway/ace/json`

### Using as a Library

#### Example: Fetching a GTFS Feed

```python
from nyctrains.mta_client import MTAClient
import asyncio

client = MTAClient()
feed_path = "nyct%2Fgtfs-ace"  # Example feed

data = asyncio.run(client.get_gtfs_feed(feed_path))
# data contains the raw protobuf bytes
print(f"Feed data length: {len(data)} bytes")
```

#### Example: Loading Static GTFS Data

```python
from nyctrains import static_gtfs

# Load static data (caches results)
stops_df = static_gtfs.get_stops()
routes_df = static_gtfs.get_routes()

if stops_df is not None:
    print(f"Loaded {len(stops_df)} stops.")
if routes_df is not None:
    print(f"Loaded {len(routes_df)} routes.")
```

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
