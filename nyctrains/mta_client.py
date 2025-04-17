import os
import httpx

MTA_API_BASE = "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/"

class MTAClient:
    def __init__(self):
        pass  # No API key needed

    async def get_gtfs_feed(self, feed_path: str):
        url = MTA_API_BASE + feed_path
        async with httpx.AsyncClient() as client:
            resp = await client.get(url)
            resp.raise_for_status()
            return resp.content
