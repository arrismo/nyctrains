from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI, HTTPException, Response
from .mta_client import MTAClient
import os
from google.transit import gtfs_realtime_pb2
from protobuf3_to_dict import protobuf_to_dict, dict_to_protobuf
from datetime import datetime, timezone
import csv

app = FastAPI()

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

# Load stop_id -> stop_name mapping at startup for subway and LIRR
STOP_ID_TO_NAME_SUBWAY = {}
with open(os.path.join(os.path.dirname(__file__), '..', 'stops.txt'), encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        STOP_ID_TO_NAME_SUBWAY[row['stop_id']] = row['stop_name']

STOP_ID_TO_NAME_LIRR = {}
lirr_path = os.path.join(os.path.dirname(__file__), '..', 'stops-lirr.txt')
if os.path.exists(lirr_path):
    with open(lirr_path, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            STOP_ID_TO_NAME_LIRR[row['stop_id']] = row['stop_name']

# Load LIRR route_id -> route_long_name mapping
ROUTE_ID_TO_LONG_NAME_LIRR = {}
routes_lirr_path = os.path.join(os.path.dirname(__file__), '..', 'routes-lirr.txt')
if os.path.exists(routes_lirr_path):
    with open(routes_lirr_path, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            ROUTE_ID_TO_LONG_NAME_LIRR[row['route_id']] = row['route_long_name']

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
async def get_feed_json(feed: str):
    if feed not in FEEDS:
        raise HTTPException(status_code=404, detail="Feed not found")
    try:
        mta = MTAClient()
        data = await mta.get_gtfs_feed(FEEDS[feed])
        feed_obj = gtfs_realtime_pb2.FeedMessage()
        feed_obj.ParseFromString(data)
        feed_dict = protobuf_to_dict(feed_obj)
        if feed == "lirr":
            feed_dict = convert_times(feed_dict, STOP_ID_TO_NAME_LIRR, ROUTE_ID_TO_LONG_NAME_LIRR)
        else:
            feed_dict = convert_times(feed_dict, STOP_ID_TO_NAME_SUBWAY)
        return feed_dict
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
