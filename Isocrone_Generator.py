import requests

from geopy.geocoders import Nominatim
import pandas


APIKEY_ORS = "5b3ce3597851110001cf624846b56f381f8742ed9d5cbf27627d9aee"


# Import data
df = pandas.read_csv("NC_derm_address_book")

# Get latitude and longitude for each location
geolocator = Nominatim(user_agent="Mapping-Access-to-Dermatological-Care-in-North-Carolina")
coordinateList = []
skipped = []
for index, row in df.iterrows():
    coordinates = geolocator.geocode(row["address_1"] + " " + row["city"] + ", " + row["state"])
    if coordinates is not None:
        coordinateList.append([coordinates.latitude, coordinates.longitude])
    else:
        skipped.append(row["Id"])
print(coordinateList)

# Post coordinates to OpenRouteService API
body = {"locations":coordinateList,"range":[300,200]}
response = requests.post('https://api.openrouteservice.org/v2/isochrones/driving-car', json=body, headers={'Authorization':APIKEY_ORS}) 
print(response.status_code, response.reason)
print(response.text)