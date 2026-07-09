import json
import math

# Load trails
with open("backend/data/trails.json", "r") as f:
    trails = json.load(f)

# Load stations
with open("backend/data/stations.json", "r") as f:
    stations = json.load(f)

# Haversine formula
def haversine(lat1, lon1, lat2, lon2):
    """Calculate the shortest distance between two coordinates. """

    R = 6371 # Radius of earth in km

    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    # c = 2 * math.asin(math.sqrt(a))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    return c * R

def find_nearest_station(trail, stations):
    """Return nearest station and distance"""

    trail_lat = trail["start_coord"][0]
    trail_lon = trail["start_coord"][1]

    nearest = None
    min_distance = float("inf")
    

    for station in stations:
        dist = haversine(
            trail_lat,
            trail_lon,
            station["lat"],
            station["long"]
        )

        if dist < min_distance:
            min_distance = dist
            nearest = station

    return nearest, min_distance

# Add nearest stations to each trail
for trail in trails:
    station, dist = find_nearest_station(trail, stations)

    trail["nearest_station"] = station["stationName"]
    trail["station_distance_km"] = round(dist, 2)
    trail["train_crsCode"] = station.get("crsCode", "unknown")
    trail["station_coord"] = [station["lat"], station["long"]]

# Save new dataset with trail + station
with open("backend/data/trails_with_stations.json", "w") as f:
    json.dump(trails, f, indent=2)

print("Trail to Station linking complete")