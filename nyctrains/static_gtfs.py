import os
import pandas as pd
from typing import Dict, Optional

# Assuming static files are in the 'resources' directory relative to project root
RESOURCE_DIR = os.path.join(os.path.dirname(__file__), '..', 'resources')

# Define expected columns for basic validation (can be expanded)
EXPECTED_COLUMNS = {
    'stops.txt': {'stop_id', 'stop_name', 'stop_lat', 'stop_lon'},
    'routes.txt': {'route_id', 'route_short_name', 'route_long_name', 'route_color'},
    'trips.txt': {'trip_id', 'route_id', 'service_id', 'trip_headsign', 'shape_id'},
    'stop_times.txt': {'trip_id', 'arrival_time', 'departure_time', 'stop_id', 'stop_sequence'},
}

# Cache loaded dataframes to avoid reloading
_loaded_data: Dict[str, Optional[pd.DataFrame]] = {}

def _load_static_file(filename: str, required: bool = True) -> Optional[pd.DataFrame]:
    """Loads a static GTFS file into a pandas DataFrame."""
    if filename in _loaded_data:
        return _loaded_data[filename]

    file_path = os.path.join(RESOURCE_DIR, filename)
    if not os.path.exists(file_path):
        if required:
            raise FileNotFoundError(f"Required static GTFS file not found: {file_path}")
        else:
            print(f"Optional static GTFS file not found: {file_path}") # pragma: no cover
            _loaded_data[filename] = None
            return None

    try:
        df = pd.read_csv(file_path, low_memory=False) # low_memory=False can help with mixed types
        
        # Basic column validation
        if filename in EXPECTED_COLUMNS:
            missing_cols = EXPECTED_COLUMNS[filename] - set(df.columns)
            if missing_cols:
                # Raise specific error for missing columns
                raise ValueError(f"Missing expected columns in {filename}: {missing_cols}")
        
        _loaded_data[filename] = df
        return df
    except ValueError as ve:
        # Check if this is the specific ValueError we raised for missing columns
        if "Missing expected columns" in str(ve):
            print(f"Validation error in {filename}: {ve}") # pragma: no cover
            raise ve # Re-raise the specific validation error
        else:
            # Treat other ValueErrors (like pandas ParserError) as generic load failures
            print(f"Error loading or parsing static GTFS file {filename}: {ve}") # pragma: no cover
            raise ValueError(f"Failed during loading or parsing of {filename}") from ve
    except Exception as e:
        # Handle other generic pandas/IO errors during load (non-ValueError)
        print(f"Error loading or parsing static GTFS file {filename}: {e}") # pragma: no cover
        raise ValueError(f"Failed during loading or parsing of {filename}") from e

def get_stops() -> Optional[pd.DataFrame]:
    """Loads stops.txt"""
    return _load_static_file('stops.txt', required=True)

def get_routes() -> Optional[pd.DataFrame]:
    """Loads routes.txt"""
    return _load_static_file('routes.txt', required=True)

def get_trips() -> Optional[pd.DataFrame]:
    """Loads trips.txt"""
    return _load_static_file('trips.txt', required=True)

def get_stop_times() -> Optional[pd.DataFrame]:
    """Loads stop_times.txt"""
    return _load_static_file('stop_times.txt', required=True)

def clear_cache():
    """Clears the cache of loaded dataframes (useful for testing)."""
    global _loaded_data
    _loaded_data = {} 