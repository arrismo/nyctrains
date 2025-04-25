import pytest
import os
import csv
from nyctrains import data_loader # Import the module to test

# Helper to create temporary CSV files
@pytest.fixture
def create_csv(tmp_path):
    def _create_csv(filename, headers, data):
        file_path = tmp_path / filename
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(data)
        return file_path
    return _create_csv

# Test successful loading
def test_load_subway_stops_success(create_csv, monkeypatch, tmp_path):
    filename = 'stops.txt'
    headers = ['stop_id', 'stop_name', 'other_col']
    data = [
        ['S01', 'Subway Stop 1', 'extra1'],
        ['S02', 'Subway Stop 2', 'extra2'],
        ['', 'Nameless Stop', 'extra3'], # Should be skipped
        ['S03', '', 'extra4'], # Should maybe be skipped depending on reqs
    ]
    create_csv(filename, headers, data)

    # Patch RESOURCE_DIR to point to tmp_path for this test
    monkeypatch.setattr(data_loader, 'RESOURCE_DIR', str(tmp_path))

    mapping = data_loader.load_subway_stops_mapping()
    assert mapping == {'S01': 'Subway Stop 1', 'S02': 'Subway Stop 2', 'S03': ''}
    assert '' not in mapping # Ensure empty key was skipped

def test_load_lirr_stops_success(create_csv, monkeypatch, tmp_path):
    filename = 'stops-lirr.txt'
    headers = ['stop_id', 'stop_name']
    data = [['L01', 'LIRR Stop 1']]
    create_csv(filename, headers, data)
    monkeypatch.setattr(data_loader, 'RESOURCE_DIR', str(tmp_path))
    mapping = data_loader.load_lirr_stops_mapping()
    assert mapping == {'L01': 'LIRR Stop 1'}

def test_load_lirr_routes_success(create_csv, monkeypatch, tmp_path):
    filename = 'routes-lirr.txt'
    headers = ['route_id', 'route_long_name']
    data = [['R1', 'LIRR Route 1']]
    create_csv(filename, headers, data)
    monkeypatch.setattr(data_loader, 'RESOURCE_DIR', str(tmp_path))
    mapping = data_loader.load_lirr_routes_mapping()
    assert mapping == {'R1': 'LIRR Route 1'}

# --- Test Error Conditions ---

def test_load_subway_stops_file_not_found(monkeypatch, tmp_path):
    # Ensure the file *doesn't* exist in tmp_path
    monkeypatch.setattr(data_loader, 'RESOURCE_DIR', str(tmp_path))
    with pytest.raises(FileNotFoundError, match=r"Required resource file not found: .*stops\.txt"):
        data_loader.load_subway_stops_mapping()

def test_load_lirr_stops_file_not_found_optional(monkeypatch, tmp_path):
    # LIRR stops are optional, should return empty dict if file not found
    monkeypatch.setattr(data_loader, 'RESOURCE_DIR', str(tmp_path))
    mapping = data_loader.load_lirr_stops_mapping()
    assert mapping == {}

def test_load_lirr_routes_file_not_found_optional(monkeypatch, tmp_path):
    # LIRR routes are optional, should return empty dict if file not found
    monkeypatch.setattr(data_loader, 'RESOURCE_DIR', str(tmp_path))
    mapping = data_loader.load_lirr_routes_mapping()
    assert mapping == {}

def test_load_subway_stops_missing_column(create_csv, monkeypatch, tmp_path):
    filename = 'stops.txt'
    headers = ['stop_id', 'wrong_name_col'] # Missing 'stop_name'
    data = [['S01', 'Stop Name']]
    create_csv(filename, headers, data)
    monkeypatch.setattr(data_loader, 'RESOURCE_DIR', str(tmp_path))
    with pytest.raises(ValueError, match=r"Missing columns in stops.txt: required.*stop_name.*found.*wrong_name_col"):
        data_loader.load_subway_stops_mapping()

def test_load_subway_stops_parsing_error(create_csv, monkeypatch, tmp_path):
    filename = 'stops.txt'
    # Simulate a non-CSV file or badly corrupted file that might cause csv.DictReader to fail
    file_path = tmp_path / filename
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write("stop_id,stop_name\n")
        f.write("S01,Valid Stop\n")
        f.write("\0") # Add a null byte to potentially cause issues

    monkeypatch.setattr(data_loader, 'RESOURCE_DIR', str(tmp_path))
    with pytest.raises(ValueError, match="Failed during processing or parsing of stops.txt"):
        data_loader.load_subway_stops_mapping()

def test_load_csv_helper_required_vs_optional(monkeypatch, tmp_path):
    monkeypatch.setattr(data_loader, 'RESOURCE_DIR', str(tmp_path))
    filename = "optional.txt"
    expected_cols = {'a', 'b'}

    # Test required=True (default) raises FileNotFoundError
    with pytest.raises(FileNotFoundError):
        data_loader._load_csv_mapping(filename, expected_cols, 'a', 'b', required=True)

    # Test required=False returns empty dict
    result = data_loader._load_csv_mapping(filename, expected_cols, 'a', 'b', required=False)
    assert result == {} 