import requests

lat, lon = -18.879, 47.507
url = f"https://rest.soilgrids.org/query?lon={lon}&lat={lat}"
data = requests.get(url).json()
print(data)