import pytest
from fastapi.testclient import TestClient
from nyctrains.main import app, get_mta_client
from nyctrains.mta_client import MTAClient
from unittest.mock import AsyncMock, patch, Mock
from google.protobuf.message import DecodeError

# Don't initialize client globally if we need to test startup errors
# client = TestClient(app)

# --- Mock MTA Client Dependency ---
@pytest.fixture
def mock_mta_client():
    mock_client = MTAClient()
    mock_client.get_gtfs_feed = AsyncMock()
    return mock_client

# Removed autouse=True, apply override manually where needed
@pytest.fixture()
def override_mta_dependency(mock_mta_client):
    def get_mock_mta():
        return mock_mta_client
    app.dependency_overrides[get_mta_client] = get_mock_mta
    yield
    app.dependency_overrides.clear()

# --- Fixture for TestClient ---
@pytest.fixture
def client(override_mta_dependency): # Apply MTA mock by default to client
    # Prevent actual static file loading during API tests by patching loaders
    # Use nested context managers for clarity and compatibility
    with patch('nyctrains.static_gtfs.get_stops', return_value=None):
        with patch('nyctrains.static_gtfs.get_routes', return_value=None):
            with patch('nyctrains.static_gtfs.get_trips', return_value=None):
                with patch('nyctrains.static_gtfs.get_stop_times', return_value=None):

                    # This client will now initialize the app, running lifespan events,
                    # but the static loaders will return None instead of hitting the disk.
                    with TestClient(app) as c:
                        # Ensure minimal mapping data is present for existing tests
                        # (Loaded before static data in the real lifespan)
                        if not hasattr(c.app.state, 'STOP_ID_TO_NAME_SUBWAY'):
                             c.app.state.STOP_ID_TO_NAME_SUBWAY = {"S1": "Stop 1"}
                        if not hasattr(c.app.state, 'STOP_ID_TO_NAME_LIRR'):
                             c.app.state.STOP_ID_TO_NAME_LIRR = {"L1": "LIRR 1"}
                        if not hasattr(c.app.state, 'ROUTE_ID_TO_LONG_NAME_LIRR'):
                             c.app.state.ROUTE_ID_TO_LONG_NAME_LIRR = {"R1": "Route 1"}
                        yield c
# --- End Fixtures ---

# === Test Startup ===
def test_startup_data_load_failure():
    """Test that the app fails to start if data loading raises an error."""
    error_message = "Fake missing stops.txt"
    # Mock the data loader function to raise an error *before* TestClient starts
    with patch('nyctrains.main.load_subway_stops_mapping', side_effect=FileNotFoundError(error_message)):
        # Expect RuntimeError when TestClient tries to start the app (lifespan)
        with pytest.raises(RuntimeError, match=f"Failed to initialize mapping data: {error_message}"):
            with TestClient(app) as c: # Initialize client within the test
                pass # Client initialization triggers startup

# === Test API Endpoints ===

@pytest.mark.parametrize("feed", [
    "ace", "bdfm", "g", "jz", "nqrw", "l", "si", "1234567", "lirr"
])
# Use the client fixture which includes the override
def test_subway_feed_json_success(feed, client, mock_mta_client):
    dummy_protobuf_bytes = b''
    mock_mta_client.get_gtfs_feed.return_value = dummy_protobuf_bytes

    response = client.get(f"/subway/{feed}/json")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)

def test_invalid_feed_returns_404(client):
    response = client.get("/subway/invalidfeed/json")
    assert response.status_code == 404
    assert response.json() == {"detail": "Feed not found"}

def test_subway_feed_json_internal_error(client, mock_mta_client):
    feed = "ace"
    error_message = "Simulated internal service error"
    mock_mta_client.get_gtfs_feed.side_effect = Exception(error_message)

    response = client.get(f"/subway/{feed}/json")

    assert response.status_code == 500
    assert "An internal error occurred" in response.json()["detail"]
    assert error_message in response.json()["detail"]

def test_subway_feed_mta_api_error(client, mock_mta_client):
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

def test_subway_feed_protobuf_parsing_error(client, mock_mta_client):
    """Test 500 error if protobuf parsing fails."""
    feed = "ace"
    invalid_protobuf_bytes = b'invalid data'
    mock_mta_client.get_gtfs_feed.return_value = invalid_protobuf_bytes

    # Target ParseFromString used within the endpoint
    with patch('nyctrains.main.gtfs_realtime_pb2.FeedMessage.ParseFromString', side_effect=DecodeError("Parsing failed")):
        response = client.get(f"/subway/{feed}/json")

    assert response.status_code == 500
    assert "An internal error occurred" in response.json()["detail"]
    assert "Parsing failed" in response.json()["detail"]

def test_subway_feed_dict_conversion_error(client, mock_mta_client):
    """Test 500 error if protobuf_to_dict fails."""
    feed = "bdfm"
    valid_protobuf_bytes = b''
    mock_mta_client.get_gtfs_feed.return_value = valid_protobuf_bytes

    # Target protobuf_to_dict used within the endpoint
    with patch('nyctrains.main.protobuf_to_dict', side_effect=TypeError("Conversion error")):
        response = client.get(f"/subway/{feed}/json")

    assert response.status_code == 500
    assert "An internal error occurred" in response.json()["detail"]
    assert "Conversion error" in response.json()["detail"]
