import time
import requests

import folium
from geopy.geocoders import Nominatim
import pandas


# Import data
df = pandas.read_csv("NC_derm_address_book")

# Get latitude and longitude for each location
geolocator = Nominatim(user_agent="Mapping-Access-to-Dermatological-Care-in-North-Carolina")
coordinateList = []
skipped = []
for index, row in df.iterrows():
    coordinates = geolocator.geocode(row["address_1"] + " " + row["city"] + ", " + row["state"])
    if row["state"] == "NC" and coordinates is not None:
        coordinateList.append([coordinates.longitude, coordinates.latitude])
    else:
        skipped.append(row["Id"])
print(coordinateList)


# Create a Folium map and cache locations to get around making several requests to ORS
m = folium.Map(location = [36.1104215233658, -79.89585490646635], zoom_start = 12)
markers = set()


# Post coordinates to OpenRouteService API and map with Folium
APIKEY_ORS = "5b3ce3597851110001cf624846b56f381f8742ed9d5cbf27627d9aee"
for coordinatePair in coordinateList:
    body = {"locations":[coordinatePair],"range":[3600]} 
    # Folium uses reversed coord pairs
    marker = folium.Marker(location = list(reversed(body["locations"][0])))
    if marker not in markers:
        response = requests.post('https://api.openrouteservice.org/v2/isochrones/driving-car', json=body, headers={'Authorization':APIKEY_ORS})
        print(response.status_code, response.reason)
        if response.status_code != 200:
            print(response.text)
        marker.add_to(m)
        markers.add(marker)
        # If the API receives too many requests it will send code 429, wait for it to reset
        if response.status_code == 429:
            time.sleep(120)
        elif response.status_code != 500:
            folium.GeoJson(response.text).add_to(m)


# Display the map
m
