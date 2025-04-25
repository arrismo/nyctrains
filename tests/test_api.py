import pytest
from fastapi.testclient import TestClient
from nyctrains.main import app, get_mta_client
from nyctrains.mta_client import MTAClient
from unittest.mock import AsyncMock

client = TestClient(app)

# --- Mock MTA Client Dependency ---
@pytest.fixture
def mock_mta_client():
    mock_client = MTAClient()
    mock_client.get_gtfs_feed = AsyncMock()
    return mock_client

@pytest.fixture(autouse=True)
def override_mta_dependency(mock_mta_client):
    def get_mock_mta():
        return mock_mta_client

    app.dependency_overrides[get_mta_client] = get_mock_mta
    yield
    app.dependency_overrides.clear()
# --- End Mock MTA Client Dependency ---

@pytest.mark.parametrize("feed", [
    "ace", "bdfm", "g", "jz", "nqrw", "l", "si", "1234567", "lirr"
])
def test_subway_feed_json_success(feed, mock_mta_client):
    dummy_protobuf_bytes = b''
    mock_mta_client.get_gtfs_feed.return_value = dummy_protobuf_bytes

    response = client.get(f"/subway/{feed}/json")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)

def test_invalid_feed_returns_404():
    response = client.get("/subway/invalidfeed/json")
    assert response.status_code == 404
    assert response.json() == {"detail": "Feed not found"}

def test_subway_feed_json_internal_error(mock_mta_client):
    feed = "ace"
    error_message = "Simulated internal service error"
    mock_mta_client.get_gtfs_feed.side_effect = Exception(error_message)

    response = client.get(f"/subway/{feed}/json")

    assert response.status_code == 500

    assert "An internal error occurred" in response.json()["detail"]
    assert error_message in response.json()["detail"]

def test_subway_feed_mta_api_error(mock_mta_client):
    feed = "bdfm"
    import httpx
    mock_mta_client.get_gtfs_feed.side_effect = httpx.HTTPStatusError(
        message="Service Unavailable",
        request=httpx.Request("GET", "dummy_url"),
        response=httpx.Response(503, request=httpx.Request("GET", "dummy_url"))
    )

    response = client.get(f"/subway/{feed}/json")
    assert response.status_code == 500
    assert "Service Unavailable" in response.json()["detail"]
