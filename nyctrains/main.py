from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI, HTTPException, Response, Depends, Request
from contextlib import asynccontextmanager
from .mta_client import MTAClient
from google.transit import gtfs_realtime_pb2
from protobuf3_to_dict import protobuf_to_dict
from datetime import datetime, timezone
from .data_loader import (
    load_subway_stops_mapping,
    load_lirr_stops_mapping,
    load_lirr_routes_mapping,
)
# Import static GTFS loading functions
from . import static_gtfs

# Define data loading within lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load data at startup
    print("Loading mapping data...") # pragma: no cover
    try:
        stop_id_to_name_subway = load_subway_stops_mapping()
        stop_id_to_name_lirr = load_lirr_stops_mapping()
        route_id_to_long_name_lirr = load_lirr_routes_mapping()
        # Store mapping data in app state
        app.state.STOP_ID_TO_NAME_SUBWAY = stop_id_to_name_subway
        app.state.STOP_ID_TO_NAME_LIRR = stop_id_to_name_lirr
        app.state.ROUTE_ID_TO_LONG_NAME_LIRR = route_id_to_long_name_lirr
        print("Mapping data loaded successfully.") # pragma: no cover
    except (FileNotFoundError, ValueError) as e:
        print(f"CRITICAL ERROR: Failed to load essential mapping data: {e}") # pragma: no cover
        raise RuntimeError(f"Failed to initialize mapping data: {e}") from e

    # Load static GTFS dataframes
    print("Loading static GTFS data...") # pragma: no cover
    try:
        app.state.stops_df = static_gtfs.get_stops()
        app.state.routes_df = static_gtfs.get_routes()
        app.state.trips_df = static_gtfs.get_trips()
        app.state.stop_times_df = static_gtfs.get_stop_times()
        # Add more processing here if needed, e.g., setting indexes
        if app.state.stops_df is not None:
            app.state.stops_df.set_index('stop_id', inplace=True)
        if app.state.routes_df is not None:
            app.state.routes_df.set_index('route_id', inplace=True)
        # etc.
        print("Static GTFS data loaded successfully.") # pragma: no cover
    except (FileNotFoundError, ValueError) as e:
        print(f"CRITICAL ERROR: Failed to load essential static GTFS data: {e}") # pragma: no cover
        # If static GTFS is critical, raise error to stop startup
        raise RuntimeError(f"Failed to initialize static GTFS data: {e}") from e

    yield
    # Clean up resources if needed on shutdown (optional)
    print("Clearing static GTFS cache...") # pragma: no cover
    static_gtfs.clear_cache() # Clear pandas cache on shutdown
    print("Application shutting down.") # pragma: no cover

# Pass lifespan to FastAPI app
app = FastAPI(lifespan=lifespan)

# Feed mapping for all major MTA subway and LIRR feeds
FEEDS = {
    "ace": "nyct%2Fgtfs-ace",
    "bdfm": "nyct%2Fgtfs-bdfm",
    "g": "nyct%2Fgtfs-g",
    "jz": "nyct%2Fgtfs-jz",
    "nqrw": "nyct%2Fgtfs-nqrw",
    "l": "nyct%2Fgtfs-l",
    "si": "nyct%2Fgtfs-si",
    "1234567": "nyct%2Fgtfs",
    "lirr": "lirr%2Fgtfs-lirr"
}

# --- Dependency Injection for MTA Client (Recommended) ---
async def get_mta_client():
    # If MTAClient needed config (like API key), it would go here
    return MTAClient()
# --- End Dependency Injection ---

def convert_times(obj, stop_mapping, route_mapping=None):
    if isinstance(obj, dict):
        new_obj = {}
        for k, v in obj.items():
            if k in ("timestamp", "time") and isinstance(v, int):
                new_obj[k] = datetime.fromtimestamp(v, tz=timezone.utc).isoformat()
            elif k == "stop_id" and isinstance(v, str):
                new_obj[k] = v
                new_obj["stop_name"] = stop_mapping.get(v, None)
            elif k == "route_id" and isinstance(v, str) and route_mapping is not None:
                new_obj[k] = v
                new_obj["route_long_name"] = route_mapping.get(v, None)
            else:
                new_obj[k] = convert_times(v, stop_mapping, route_mapping)
        return new_obj
    elif isinstance(obj, list):
        return [convert_times(item, stop_mapping, route_mapping) for item in obj]
    else:
        return obj

@app.get("/subway/{feed}/json")
async def get_feed_json(feed: str, request: Request, mta: MTAClient = Depends(get_mta_client)):
    if feed not in FEEDS:
        raise HTTPException(status_code=404, detail="Feed not found")
    try:
        data = await mta.get_gtfs_feed(FEEDS[feed])
        feed_obj = gtfs_realtime_pb2.FeedMessage()
        feed_obj.ParseFromString(data)
        feed_dict = protobuf_to_dict(feed_obj)

        # Determine which mappings to use (retrieve from app.state)
        stop_mapping = request.app.state.STOP_ID_TO_NAME_LIRR if feed == "lirr" else request.app.state.STOP_ID_TO_NAME_SUBWAY
        route_mapping = request.app.state.ROUTE_ID_TO_LONG_NAME_LIRR if feed == "lirr" else None

        processed_dict = convert_times(feed_dict, stop_mapping, route_mapping)
        return processed_dict
    except HTTPException: # Don't catch HTTPExceptions raised intentionally
        raise
    except Exception as e:
        # Log the exception details for debugging
        print(f"Unhandled exception in get_feed_json for feed '{feed}': {e}") # pragma: no cover
        # Consider logging traceback: import traceback; traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"An internal error occurred: {e}")
