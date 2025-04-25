import os
import csv
from typing import Dict, Tuple, Set

RESOURCE_DIR = os.path.join(os.path.dirname(__file__), '..', 'resources')

def _load_csv_mapping(
    filename: str,
    expected_columns: Set[str],
    key_column: str,
    value_column: str,
    required: bool = True,
) -> Dict[str, str]:
    """Helper function to load mappings from a CSV file."""
    file_path = os.path.join(RESOURCE_DIR, filename)
    mapping = {}
    if not os.path.exists(file_path):
        if required:
            # Or raise specific custom exception
            raise FileNotFoundError(f"Required resource file not found: {file_path}")
        else:
            # Optionally log a warning here
            return mapping # Return empty if optional and not found

    try:
        with open(file_path, encoding='utf-8') as f:
            reader = csv.DictReader(f)
            # Perform column check *before* iterating rows within the main try-except
            if not expected_columns.issubset(reader.fieldnames or []):
                raise ValueError(
                    f"Missing columns in {filename}: required {expected_columns}, found {reader.fieldnames}"
                )
            # Now iterate through rows, catching potential errors during iteration/processing
            for row in reader:
                # Basic validation, could add more checks
                if key_column in row and value_column in row and row[key_column]:
                    mapping[row[key_column]] = row[value_column]
                else:
                    # Optionally log a warning for bad rows
                    pass
    except ValueError as ve:
        # Allow the specific ValueError for missing columns to propagate directly
        raise ve
    except Exception as e:
        # Catch other *unexpected* errors during file opening or processing
        print(f"Error processing {filename}: {e}")
        # Use a more specific message for these unexpected errors
        raise ValueError(f"Failed during processing or parsing of {filename}") from e

    return mapping


def load_subway_stops_mapping() -> Dict[str, str]:
    """Loads the stop_id -> stop_name mapping for subways."""
    return _load_csv_mapping(
        filename='stops.txt',
        expected_columns={'stop_id', 'stop_name'},
        key_column='stop_id',
        value_column='stop_name',
        required=True
    )

def load_lirr_stops_mapping() -> Dict[str, str]:
    """Loads the stop_id -> stop_name mapping for LIRR."""
    # Assuming stops-lirr.txt might be optional or added later
    return _load_csv_mapping(
        filename='stops-lirr.txt',
        expected_columns={'stop_id', 'stop_name'},
        key_column='stop_id',
        value_column='stop_name',
        required=False # Set to True if it's mandatory
    )

def load_lirr_routes_mapping() -> Dict[str, str]:
    """Loads the route_id -> route_long_name mapping for LIRR."""
    # Assuming routes-lirr.txt might be optional or added later
    return _load_csv_mapping(
        filename='routes-lirr.txt',
        expected_columns={'route_id', 'route_long_name'},
        key_column='route_id',
        value_column='route_long_name',
        required=False # Set to True if it's mandatory
    ) 