import requests
import json
import datetime
from contextlib import redirect_stdout
from google.transit import gtfs_realtime_pb2

# Get MTA ACE Train Data
# MTA train data is returned in a Protocol Buffer format (GTFS format)
response = requests.get("https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-ace")
feed = gtfs_realtime_pb2.FeedMessage()
feed.ParseFromString(response.content)
print(feed)
