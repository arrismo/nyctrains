from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI, HTTPException, Response
from .mta_client import MTAClient
import os
from google.transit import gtfs_realtime_pb2
from protobuf3_to_dict import protobuf_to_dict, dict_to_protobuf
from datetime import datetime, timezone

app = FastAPI()

def convert_times(obj):
    if isinstance(obj, dict):
        new_obj = {}
        for k, v in obj.items():
            if k in ("timestamp", "time") and isinstance(v, int):
                new_obj[k] = datetime.fromtimestamp(v, tz=timezone.utc).isoformat()
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
