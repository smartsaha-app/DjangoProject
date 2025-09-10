# SmartSaha/services/soil_service.py
import requests

OPEN_EPI_URL = "https://api.openepi.io/soil/property"

def get_soil_data(longitude, latitude):
    url = (
        f"{OPEN_EPI_URL}?lon={longitude}&lat={latitude}"
        "&depths=0-5cm"
        "&properties=bdod"
        "&properties=phh2o"
        "&properties=nitrogen"
        "&properties=soc"
        "&properties=cec"
        "&properties=cfvo"
        "&properties=clay"
        "&properties=sand"
        "&properties=silt"
        "&values=mean"
    )
    response = requests.get(url, timeout=20)
    response.raise_for_status()
    return response.json()
