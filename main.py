

import requests
import json
import datetime
from contextlib import redirect_stdout
from google.transit import gtfs_realtime_pb2
from protobuf3_to_dict import protobuf_to_dict

# Get MTA ACE Train Data
# MTA train data is returned in a Protocol Buffer format (GTFS format)
response = requests.get("https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-ace")
feed = gtfs_realtime_pb2.FeedMessage()
feed.ParseFromString(response.content)
feed_dict = protobuf_to_dict(feed)
# #print(feed_dict)
dump_object = json.dumps(feed_dict, indent=4)
# # Save out data to json file -- temporary 
# with open('a-train-data.json','w') as f:
#    with redirect_stdout(f):`
#       print(dump_object)


import csv
import pandas as pd

def load_stop_names(csv_file):
    """Load stop ID to name mapping from CSV file"""
    stop_names = {}
    try:
        # Read CSV file using pandas
        df = pd.read_csv(csv_file)
        # Create dictionary mapping stop_id to stop_name
        stop_names = dict(zip(df['stop_id'], df['stop_name']))
    except Exception as e:
        print(f"Error loading stop names: {str(e)}")
    return stop_names

def convert_to_readable_time(timestamp):
    """Convert Unix timestamp to readable datetime string"""
    dt = datetime.datetime.fromtimestamp(timestamp)
    return dt.strftime('%Y-%m-%d %H:%M:%S')

def convert_start_date(date_str):
    """Convert YYYYMMDD format to readable date string"""
    dt = datetime.datetime.strptime(date_str, '%Y%m%d')
    return dt.strftime('%Y-%m-%d')

def modify_transit_times(data, stop_names):
    """Modify transit times and stop IDs in the JSON data structure"""
    modified_data = json.loads(json.dumps(data))
    
    # Update header timestamp
    if "header" in modified_data:
        header_time = modified_data["header"]["timestamp"]
        if isinstance(header_time, (int, float)):
            modified_data["header"]["timestamp"] = convert_to_readable_time(header_time)
    
    for entity in modified_data.get("entity", []):
        # Handle trip updates
        trip_update = entity.get("trip_update")
        if trip_update:
            # Modify trip information
            if "trip" in trip_update and "start_date" in trip_update["trip"]:
                original_date = trip_update["trip"]["start_date"]
                if len(original_date) == 8:  # YYYYMMDD format
                    trip_update["trip"]["start_date"] = convert_start_date(original_date)
            
            # Modify stop times and names
            for stop_time in trip_update.get("stop_time_update", []):
                # Replace stop ID with name
                if "stop_id" in stop_time:
                    stop_id = stop_time["stop_id"]
                    if stop_id in stop_names:
                        stop_time["stop_id"] = stop_names[stop_id]
                
                # Modify arrival time
                if "arrival" in stop_time and "time" in stop_time["arrival"]:
                    original_time = stop_time["arrival"]["time"]
                    if isinstance(original_time, (int, float)):
                        stop_time["arrival"]["time"] = convert_to_readable_time(original_time)
                
                # Modify departure time
                if "departure" in stop_time and "time" in stop_time["departure"]:
                    original_time = stop_time["departure"]["time"]
                    if isinstance(original_time, (int, float)):
                        stop_time["departure"]["time"] = convert_to_readable_time(original_time)
        
        # Handle vehicle updates
        vehicle = entity.get("vehicle")
        if vehicle:
            # Replace stop ID with name in vehicle update
            if "stop_id" in vehicle:
                stop_id = vehicle["stop_id"]
                if stop_id in stop_names:
                    vehicle["stop_id"] = stop_names[stop_id]
            
            # Modify vehicle timestamp
            if "timestamp" in vehicle:
                vehicle_time = vehicle["timestamp"]
                if isinstance(vehicle_time, (int, float)):
                    vehicle["timestamp"] = convert_to_readable_time(vehicle_time)
            
            # Modify trip information in vehicle update
            if "trip" in vehicle and "start_date" in vehicle["trip"]:
                original_date = vehicle["trip"]["start_date"]
                if len(original_date) == 8:  # YYYYMMDD format
                    vehicle["trip"]["start_date"] = convert_start_date(original_date)
    
    return modified_data

def load_and_modify_json(input_file, output_file, stops_csv):
    """Load JSON file, modify times and stop names, and save to new file"""
    try:
        # Load stop names from CSV
        stop_names = load_stop_names(stops_csv)
        
        # Read the JSON file
        with open(input_file, 'r') as f:
            data = json.load(f)
        
        # Modify the times and stop names
        modified_data = modify_transit_times(data, stop_names)
        
        # Save the modified JSON
        with open(output_file, 'w') as f:
            json.dump(modified_data, f, indent=4)
            
        print(f"\nSuccessfully modified times and stop names, saved to {output_file}")
        
    except FileNotFoundError:
        print(f"Error: Could not find input file {input_file}")
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in {input_file}")
    except Exception as e:
        print(f"Error: An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    load_and_modify_json(
        input_file='raw-ace-data.json',
        output_file='modified_transit_times.json',
        stops_csv='stops.csv'  # Add your stops CSV file name here
    )