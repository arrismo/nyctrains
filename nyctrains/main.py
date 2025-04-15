from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI, HTTPException, Response
from .mta_client import MTAClient
import os
from google.transit import gtfs_realtime_pb2
from protobuf3_to_dict import protobuf_to_dict, dict_to_protobuf

app = FastAPI()

@app.get("/subway/ace/json")
async def get_ace_feed_json():
    try:
        mta = MTAClient()
        data = await mta.get_gtfs_feed("nyct%2Fgtfs-ace")
        feed = gtfs_realtime_pb2.FeedMessage()
        feed.ParseFromString(data)
        # Convert the full feed to a dict (full dump)
        feed_dict = protobuf_to_dict(feed)
        return feed_dict
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
