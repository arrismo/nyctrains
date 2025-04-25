import pytest
import httpx
import respx
from nyctrains.mta_client import MTAClient, MTA_API_BASE

@pytest.mark.asyncio
async def test_mta_client_get_gtfs_feed_success():
    """Test successful retrieval of a GTFS feed."""
    feed_path = "nyct%2Fgtfs-ace"
    expected_url = MTA_API_BASE + feed_path
    dummy_content = b'protobuf-data-ace'

    # Mock the HTTP request using respx
    with respx.mock:
        respx.get(expected_url).mock(return_value=httpx.Response(200, content=dummy_content))

        client = MTAClient()
        content = await client.get_gtfs_feed(feed_path)

        assert content == dummy_content

@pytest.mark.asyncio
async def test_mta_client_get_gtfs_feed_http_error():
    """Test handling of HTTP errors from the MTA API."""
    feed_path = "nyct%2Fgtfs-bdfm"
    expected_url = MTA_API_BASE + feed_path

    # Mock the HTTP request to return a 404 error
    with respx.mock:
        respx.get(expected_url).mock(return_value=httpx.Response(404))

        client = MTAClient()

        # Assert that httpx.HTTPStatusError is raised
        with pytest.raises(httpx.HTTPStatusError) as exc_info:
            await client.get_gtfs_feed(feed_path)

        # Optionally check the status code on the exception
        assert exc_info.value.response.status_code == 404

@pytest.mark.asyncio
async def test_mta_client_get_gtfs_feed_request_error():
    """Test handling of network/request errors."""
    feed_path = "nyct%2Fgtfs-g"
    expected_url = MTA_API_BASE + feed_path

    # Mock the HTTP request to raise a network error
    with respx.mock:
        respx.get(expected_url).mock(side_effect=httpx.RequestError("Network error"))

        client = MTAClient()

        # Assert that httpx.RequestError is raised (or its subclass)
        with pytest.raises(httpx.RequestError):
            await client.get_gtfs_feed(feed_path) 