# SmartSaha/services/climate_service.py
import requests

NASA_API_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"


def get_climate_data(longitude, latitude, start, end):
    url = (
        f"{NASA_API_URL}?parameters="
        "T2M,T2MDEW,T2MWET,TS,T2M_RANGE,T2M_MAX,T2M_MIN,"
        "PRECTOTCORR,EVLAND,GWETPROF"
        f"&community=RE&longitude={longitude}&latitude={latitude}"
        f"&start={start}&end={end}&format=JSON"
    )
    response = requests.get(url, timeout=20)
    response.raise_for_status()
    return response.json()
