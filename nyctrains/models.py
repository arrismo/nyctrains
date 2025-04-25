from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

# --- Models for Enhanced Endpoints ---

class StopTimeUpdate(BaseModel):
    stop_id: str
    stop_name: Optional[str] = None
    arrival_time: Optional[datetime] = None
    departure_time: Optional[datetime] = None
    scheduled_arrival_time: Optional[str] = None # Example: Store as string HH:MM:SS
    scheduled_departure_time: Optional[str] = None # Example: Store as string HH:MM:SS
    delay_seconds: Optional[int] = None

class TripArrivalInfo(BaseModel):
    route_id: str
    route_short_name: Optional[str] = None
    route_long_name: Optional[str] = None
    route_color: Optional[str] = None
    trip_id: str
    trip_headsign: Optional[str] = None
    direction_id: Optional[int] = None # Requires trips.txt processing
    updates: List[StopTimeUpdate]

class StopArrivalsResponse(BaseModel):
    stop_id: str
    stop_name: Optional[str] = None
    arrivals: List[TripArrivalInfo]
    last_updated: datetime

class VehiclePosition(BaseModel):
    vehicle_id: str
    trip_id: Optional[str] = None
    route_id: Optional[str] = None
    route_short_name: Optional[str] = None
    latitude: float
    longitude: float
    bearing: Optional[float] = None
    speed_mps: Optional[float] = Field(None, alias="speed") # Example alias
    current_stop_sequence: Optional[int] = None
    current_status: Optional[str] = None # e.g., IN_TRANSIT_TO, STOPPED_AT
    timestamp: datetime

class RouteVehiclesResponse(BaseModel):
    route_id: str
    route_short_name: Optional[str] = None
    vehicles: List[VehiclePosition]
    last_updated: datetime

class ServiceAlert(BaseModel):
    alert_id: str # Usually derived from the GTFS-RT entity id
    active_period_start: Optional[datetime] = None
    active_period_end: Optional[datetime] = None
    informed_entity: List[Dict[str, Any]] # Route, stop, etc. affected
    cause: Optional[str] = None
    effect: Optional[str] = None
    header_text: Optional[str] = None
    description_text: Optional[str] = None
    url: Optional[str] = None

class AlertsResponse(BaseModel):
    alerts: List[ServiceAlert]
    last_updated: datetime

# --- Model for Original Endpoint (Optional Enhancement) ---
# You could potentially define a model for the full GTFS feed structure
# but it can be quite complex. Returning the raw dict might be simpler.
# class FeedMessageModel(BaseModel):
#    header: Dict[str, Any]
#    entity: List[Dict[str, Any]] 