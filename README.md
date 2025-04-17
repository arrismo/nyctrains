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

**Note:** You can adapt this example to visualize arrival times, delays, or other GTFS-RT data fields using pandas and matplotlib/seaborn.

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

### 3. Run the FastAPI server
```bash
uvicorn nyctrains.main:app --reload
```

### 4. Access the API
- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- Example: [http://localhost:8000/subway/ace/json](http://localhost:8000/subway/ace/json)
- Example: [http://localhost:8000/subway/lirr/json](http://localhost:8000/subway/lirr/json)

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