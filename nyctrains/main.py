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

# Load stop_id -> stop_name mapping at startup
STOP_ID_TO_NAME = {}
with open(os.path.join(os.path.dirname(__file__), '..', 'stops.txt'), encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        STOP_ID_TO_NAME[row['stop_id']] = row['stop_name']

def convert_times(obj):
    if isinstance(obj, dict):
        new_obj = {}
        for k, v in obj.items():
            if k in ("timestamp", "time") and isinstance(v, int):
                new_obj[k] = datetime.fromtimestamp(v, tz=timezone.utc).isoformat()
            elif k == "stop_id" and isinstance(v, str):
                new_obj[k] = v
                new_obj["stop_name"] = STOP_ID_TO_NAME.get(v, None)
            else:
                new_obj[k] = convert_times(v)
        return new_obj
    elif isinstance(obj, list):
        return [convert_times(item) for item in obj]
    else:
        return obj

@app.get("/subway/ace/json")
async def get_ace_feed_json():
    try:
        mta = MTAClient()
        data = await mta.get_gtfs_feed("nyct%2Fgtfs-ace")
        feed = gtfs_realtime_pb2.FeedMessage()
        feed.ParseFromString(data)
        feed_dict = protobuf_to_dict(feed)
        feed_dict = convert_times(feed_dict)
        return feed_dict
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
