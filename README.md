# nyctrains API
[![Python Versions](https://img.shields.io/pypi/pyversions/nyctrains.svg)](https://pypi.python.org/pypi/nyctrains)
[![PyPI](https://img.shields.io/pypi/v/nyctrains)](https://pypi.org/project/nyctrains/#history)
[![PyPI Downloads](https://img.shields.io/pypi/dm/nyctrains)](https://pypistats.org/packages/nyctrains)
[![Repo Status](https://www.repostatus.org/badges/latest/active.svg)](https://www.repostatus.org/#active)
[![codecov](https://codecov.io/gh/arrismo/nyctrains/graph/badge.svg?token=AGXZZYUQU3)](https://codecov.io/gh/arrismo/nyctrains)
[![CI Build](https://github.com/arrismo/nyctrains/actions/workflows/ci-tests.yaml/badge.svg)](https://github.com/arrismo/nyctrains/actions/workflows/ci-tests.yaml)

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

## Installation

Install using pip:

```sh
pip install nyctrains
```

## Usage

This package provides Python tools and a FastAPI backend for working with MTA GTFS-RT subway and LIRR data. **No API key is required** to use the package or access the feeds.

### Example: Fetching a GTFS Feed

```python
from nyctrains.mta_client import MTAClient
import asyncio

client = MTAClient()
feed_path = "nyct%2Fgtfs-ace"  # Example feed

data = asyncio.run(client.get_gtfs_feed(feed_path))
print(f"Feed data length: {len(data)} bytes")
```

### Example: Visualizing Subway Feed Data

You can use `matplotlib` and `pandas` to visualize GTFS-RT feed data. Below is a simple example that counts and plots the number of train trip updates in a feed:

```python
import asyncio
import pandas as pd
import matplotlib.pyplot as plt
from nyctrains.mta_client import MTAClient
from google.transit import gtfs_realtime_pb2
from protobuf3_to_dict import protobuf_to_dict, dict_to_protobuf

client = MTAClient()
feed_path = "nyct%2Fgtfs-ace"

def parse_trip_updates(feed_bytes):
    feed = gtfs_realtime_pb2.FeedMessage()
    feed.ParseFromString(feed_bytes)
    feed_dict = protobuf_to_dict(feed)
    trip_updates = [e for e in feed_dict['entity'] if 'trip_update' in e]
    return trip_updates

# Fetch and parse feed
data = asyncio.run(client.get_gtfs_feed(feed_path))
trip_updates = parse_trip_updates(data)

# Convert to DataFrame for analysis
trip_ids = [tu['trip_update']['trip']['trip_id'] for tu in trip_updates]
df = pd.DataFrame({"trip_id": trip_ids})

# Plot number of unique trips
plt.figure(figsize=(8, 4))
df["trip_id"].value_counts().plot(kind="bar")
plt.title("Number of Trip Updates per Trip ID")
plt.xlabel("Trip ID")
plt.ylabel("Update Count")
plt.tight_layout()
plt.show()
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

## Data Resources
- All static mapping files are in the `resources/` directory:
  - `resources/stops.txt` (NYC Subway stops)
  - `resources/stops-lirr.txt` (LIRR stops)
  - `resources/routes-lirr.txt` (LIRR route names)
