import pytest
import pandas as pd
import os
from nyctrains import static_gtfs
from unittest.mock import patch # Using unittest.mock patch alongside monkeypatch

# Helper fixture to create dummy CSV files
@pytest.fixture
def create_dummy_gtfs(tmp_path):
    files = {}
    base_path = tmp_path

    def _create_file(filename, headers, data):
        file_path = base_path / filename
        df = pd.DataFrame(data, columns=headers)
        df.to_csv(file_path, index=False)
        files[filename] = file_path
        return file_path

    # Create dummy versions of expected files
    _create_file('stops.txt', ['stop_id', 'stop_name', 'stop_lat', 'stop_lon'], [['s1', 'Stop 1', 40.0, -74.0]])
    _create_file('routes.txt', ['route_id', 'route_short_name', 'route_long_name', 'route_color'], [['r1', '1', 'Route 1', 'FF0000']])
    _create_file('trips.txt', ['trip_id', 'route_id', 'service_id', 'trip_headsign', 'shape_id'], [['t1', 'r1', 'sv1', 'Downtown', 'sh1']])
    _create_file('stop_times.txt', ['trip_id', 'arrival_time', 'departure_time', 'stop_id', 'stop_sequence'], [['t1', '08:00:00', '08:00:30', 's1', 1]])

    return base_path # Return the temp directory path

# Fixture to setup mocks and clear cache before/after each test
@pytest.fixture(autouse=True)
def manage_static_loader(monkeypatch, tmp_path):
    # Patch the resource directory to point to tmp_path
    monkeypatch.setattr(static_gtfs, 'RESOURCE_DIR', str(tmp_path))
    # Clear cache before test
    static_gtfs.clear_cache()
    yield
    # Clear cache after test
    static_gtfs.clear_cache()

# --- Test Successful Loading ---
def test_get_stops_success(create_dummy_gtfs):
    df = static_gtfs.get_stops()
    assert isinstance(df, pd.DataFrame)
    assert list(df.columns) == ['stop_id', 'stop_name', 'stop_lat', 'stop_lon']
    assert df.iloc[0]['stop_id'] == 's1'

def test_get_routes_success(create_dummy_gtfs):
    df = static_gtfs.get_routes()
    assert isinstance(df, pd.DataFrame)
    assert list(df.columns) == ['route_id', 'route_short_name', 'route_long_name', 'route_color']
    assert df.iloc[0]['route_id'] == 'r1'

def test_get_trips_success(create_dummy_gtfs):
    df = static_gtfs.get_trips()
    assert isinstance(df, pd.DataFrame)
    assert list(df.columns) == ['trip_id', 'route_id', 'service_id', 'trip_headsign', 'shape_id']
    assert df.iloc[0]['trip_id'] == 't1'

def test_get_stop_times_success(create_dummy_gtfs):
    df = static_gtfs.get_stop_times()
    assert isinstance(df, pd.DataFrame)
    assert list(df.columns) == ['trip_id', 'arrival_time', 'departure_time', 'stop_id', 'stop_sequence']
    assert df.iloc[0]['trip_id'] == 't1'

# --- Test Error Conditions ---
def test_load_required_file_not_found(tmp_path): # Don't create dummy files
    # RESOURCE_DIR is already patched by manage_static_loader fixture
    with pytest.raises(FileNotFoundError, match=r"Required static GTFS file not found: .*stops\.txt"):
        static_gtfs.get_stops()

def test_load_missing_columns(create_dummy_gtfs, tmp_path):
    # Overwrite stops.txt with missing columns
    bad_file_path = tmp_path / 'stops.txt'
    bad_df = pd.DataFrame([['s1', 'Stop 1']], columns=['stop_id', 'stop_name']) # Missing lat/lon
    bad_df.to_csv(bad_file_path, index=False)

    with pytest.raises(ValueError, match=r"Missing expected columns in stops\.txt:.*stop_(lat|lon).*"):
        static_gtfs.get_stops()

def test_load_parsing_error(tmp_path):
    # Create a file with correct headers but data that pandas cannot parse
    filename = 'routes.txt'
    bad_file_path = tmp_path / filename
    with open(bad_file_path, 'w') as f:
        # Write correct headers
        headers = static_gtfs.EXPECTED_COLUMNS[filename]
        f.write(",".join(headers) + "\n")
        # Write some valid data
        f.write("r1,1,Route 1,FF0000\n")
        # Write invalid data likely to cause a CParserError or similar pandas error
        f.write('r2,2,"Malformed route name with unclosed quote,more,fields\n')

    # Expect the generic error message from the final except block
    with pytest.raises(ValueError, match=r"Failed during loading or parsing of routes\.txt"):
        static_gtfs.get_routes()

# --- Test Caching --- 
def test_caching(create_dummy_gtfs):
    df1 = static_gtfs.get_stops()
    df2 = static_gtfs.get_stops()
    assert df1 is df2 # Should be the exact same object due to cache

    # Clear cache and reload
    static_gtfs.clear_cache()
    df3 = static_gtfs.get_stops()
    assert df1 is not df3 # Should be a new object after cache clear
    pd.testing.assert_frame_equal(df1, df3) # Data should be the same

def test_optional_file_not_found(tmp_path): # Don't create dummy files
    # Test _load_static_file directly for optional case
    df = static_gtfs._load_static_file('optional_file.txt', required=False)
    assert df is None 