import pytest
from fastapi.testclient import TestClient
from nyctrains.main import app

client = TestClient(app)

@pytest.mark.parametrize("feed", [
    "ace", "bdfm", "g", "jz", "nqrw", "l", "si", "1234567", "lirr"
])
def test_subway_feed_json(feed):
    response = client.get(f"/subway/{feed}/json")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert any(k in data for k in ("entity", "trip_update", "nyct_subway_version", "gtfs_realtime_version"))

def test_subway_ace_json():
    response = client.get("/subway/ace/json")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    # Updated: Check for actual keys like 'entity' or 'trip_update'
    assert any(k in data for k in ("entity", "trip_update", "nyct_subway_version", "gtfs_realtime_version"))

def test_subway_lirr_json():
    response = client.get("/subway/lirr/json")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert any(k in data for k in ("entity", "trip_update", "nyct_subway_version", "gtfs_realtime_version"))

def test_invalid_line_returns_error():
    response = client.get("/subway/invalidline/json")
    # Accept either 404 or 422 depending on your implementation
    assert response.status_code in (404, 422)
