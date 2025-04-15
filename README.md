# nyctrains-dashboard

A FastAPI-based backend for working with the MTA's real-time subway GTFS-RT data feeds. This project fetches, parses, and exposes the ACE line's real-time feed as human-readable JSON.

## Features
- Proxies and parses the MTA GTFS-RT feed for the ACE subway line
- Converts all Unix timestamps to ISO 8601 strings for easy reading
- Provides a `/subway/ace/json` endpoint for full feed access
- Ready for extension to other subway lines or custom endpoints

## Quickstart

### 1. Clone the repository
```bash
git clone https://github.com/arrismo/nyctrains.git
cd nyctrains
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
# or if using uv/pyproject.toml:
uv pip install -r requirements.txt
```

### 3. Set up your MTA API key
Create a `.env` file in the project root:
```
MTA_API_KEY=your-mta-api-key-here
```

### 4. Run the FastAPI server
```bash
uvicorn nyctrains.main:app --reload
```

### 5. Access the API
- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- Human-readable JSON: [http://localhost:8000/subway/ace/json](http://localhost:8000/subway/ace/json)

## Example Output
```json
{
  "header": {
    "gtfs_realtime_version": "1.0",
    "timestamp": "2025-04-15T19:19:46+00:00"
  },
  "entity": [
    {
      "id": "000001A",
      "trip_update": {
        "trip": { ... },
        "stop_time_update": [
          {
            "arrival": { "time": "2025-04-15T19:19:37+00:00" },
            ...
          }
        ]
      }
    }
  ]
}
```

## Development
- All main code is in the `nyctrains/` package.
- See `main.py` for API endpoints and `mta_client.py` for MTA API access logic.
- Extend or customize endpoints as needed!