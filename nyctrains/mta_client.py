import os
import httpx

MTA_API_BASE = "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/"

class MTAClient:
    def __init__(self, api_key: str = None):
        self.api_key = os.getenv("MTA_API_KEY")
        if not self.api_key:
            raise ValueError("MTA_API_KEY must be set as an environment variable or provided explicitly.")

    async def get_gtfs_feed(self, feed_path: str):
        url = MTA_API_BASE + feed_path
        headers = {"x-api-key": self.api_key}
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=headers)
            resp.raise_for_status()
            return resp.content
