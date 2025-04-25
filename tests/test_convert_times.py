import pytest
from nyctrains.main import convert_times # Function to test
from datetime import datetime, timezone

# Sample mappings for testing
STOP_MAP = {
    "S01": "Subway Stop One",
    "S02": "Subway Stop Two",
    "L01": "LIRR Stop One"
}
ROUTE_MAP = {
    "R1": "LIRR Route One",
    "R2": "LIRR Route Two"
}

# Test cases using pytest.mark.parametrize
@pytest.mark.parametrize("input_data, stop_mapping, route_mapping, expected_output", [
    # Case 1: Basic time conversion
    (
        {"timestamp": 1678886400, "value": 123},
        STOP_MAP, None,
        {"timestamp": "2023-03-15T13:20:00+00:00", "value": 123}
    ),
    # Case 2: List of dicts with time and stop_id
    (
        [
            {"time": 1678886460, "stop_id": "S01"},
            {"time": 1678886520, "stop_id": "S02"}
        ],
        STOP_MAP, None,
        [
            {"time": "2023-03-15T13:21:00+00:00", "stop_id": "S01", "stop_name": "Subway Stop One"},
            {"time": "2023-03-15T13:22:00+00:00", "stop_id": "S02", "stop_name": "Subway Stop Two"}
        ]
    ),
    # Case 3: Nested structure with stops and routes (LIRR style)
    (
        {
            "header": {"timestamp": 1678886580},
            "entity": [
                {
                    "trip_update": {
                        "trip": {"route_id": "R1"},
                        "stop_time_update": [
                            {"stop_id": "L01", "arrival": {"time": 1678886640}},
                            {"stop_id": "L02", "departure": {"time": 1678886700}} # L02 not in map
                        ]
                    }
                }
            ]
        },
        STOP_MAP, ROUTE_MAP,
        {
            "header": {"timestamp": "2023-03-15T13:23:00+00:00"},
            "entity": [
                {
                    "trip_update": {
                        "trip": {"route_id": "R1", "route_long_name": "LIRR Route One"},
                        "stop_time_update": [
                            {"stop_id": "L01", "stop_name": "LIRR Stop One", "arrival": {"time": "2023-03-15T13:24:00+00:00"}},
                            {"stop_id": "L02", "stop_name": None, "departure": {"time": "2023-03-15T13:25:00+00:00"}}
                        ]
                    }
                }
            ]
        }
    ),
    # Case 4: Input is not a dict or list
    (
        "just a string",
        STOP_MAP, None,
        "just a string"
    ),
    # Case 5: Empty dictionary
    (
        {},
        STOP_MAP, ROUTE_MAP,
        {}
    ),
    # Case 6: Empty list
    (
        [],
        STOP_MAP, ROUTE_MAP,
        []
    ),
    # Case 7: Stop ID not found in mapping
    (
        {"stop_id": "S99"},
        STOP_MAP, None,
        {"stop_id": "S99", "stop_name": None}
    ),
    # Case 8: Route ID not found in mapping
    (
        {"route_id": "R99"},
        STOP_MAP, ROUTE_MAP,
        {"route_id": "R99", "route_long_name": None}
    ),
    # Case 9: Route mapping not provided, route_id should pass through
    (
        {"route_id": "R1"},
        STOP_MAP, None, # No route map passed
        {"route_id": "R1"} # No route_long_name added
    ),
])
def test_convert_times(input_data, stop_mapping, route_mapping, expected_output):
    """Test the convert_times function with various inputs."""
    result = convert_times(input_data, stop_mapping, route_mapping)
    assert result == expected_output 