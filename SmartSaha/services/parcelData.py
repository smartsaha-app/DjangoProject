from functools import lru_cache

import requests
from django.utils import timezone

from SmartSaha.models import Parcel, SoilData, ClimateData, YieldRecord


class ParcelDataService:

    @staticmethod
    def get_first_point(parcel: Parcel):
        if not parcel.points or len(parcel.points) == 0:
            raise ValueError("Parcel has no points")
        return parcel.points[0]

    @staticmethod
    def fetch_soil(parcel: Parcel) -> SoilData | None:
        """
        Récupère les données du sol pour une parcelle.
        - Vérifie la dernière entrée existante.
        - Si mean non-null, retourne l'objet existant.
        - Sinon, itère sur tous les points pour trouver des données valides.
        - Si aucun point n'est valide, prend le dernier point et l'enregistre.
        """
        soil_data_obj = SoilData.objects.filter(parcel=parcel).order_by('-created_at').last()

        def has_non_null_mean(data: dict) -> bool:
            return any(
                d["values"]["mean"] is not None
                for layer in data.get("properties", {}).get("layers", [])
                for d in layer.get("depths", [])
            )

        # Si déjà existant et valide
        if soil_data_obj and has_non_null_mean(soil_data_obj.data):
            return soil_data_obj

        points = parcel.points
        last_data = None  # stocke le dernier point pour fallback

        for point in points:
            lat, lon = point["lat"], point["lng"]
            print(f"lat: {lat}, lon: {lon}")
            url = (
                f"https://rest.isric.org/soilgrids/v2.0/properties/query?"
                f"lon={lon}&lat={lat}&property=phh2o&property=soc&property=nitrogen"
                f"&property=sand&property=clay&property=silt&depth=0-5cm&value=mean"
            )

            try:
                resp = requests.get(url, timeout=60)
                resp.raise_for_status()
                data = resp.json()
                last_data = data  # toujours stocker le dernier

                if has_non_null_mean(data):
                    # Conversion des d_factor
                    for layer in data["properties"]["layers"]:
                        factor = layer.get("unit_measure", {}).get("d_factor", 1)
                        for d in layer["depths"]:
                            if d["values"]["mean"] is not None:
                                d["values"]["mean"] = d["values"]["mean"] / factor

                    # Update ou création
                    if soil_data_obj:
                        soil_data_obj.data = data
                        soil_data_obj.save()
                        return soil_data_obj
                    else:
                        return SoilData.objects.create(parcel=parcel, data=data)

            except requests.RequestException as e:
                print(f"[ERROR] SoilGrids API failed for point ({lat}, {lon}): {e}")
                continue

        # Aucun point valide trouvé, fallback sur le dernier point
        if last_data:
            # Conversion d_factor même si tout null
            for layer in last_data["properties"]["layers"]:
                factor = layer.get("unit_measure", {}).get("d_factor", 1)
                for d in layer["depths"]:
                    if d["values"]["mean"] is not None:
                        d["values"]["mean"] = d["values"]["mean"] / factor

            if soil_data_obj:
                soil_data_obj.data = last_data
                soil_data_obj.save()
                return soil_data_obj
            else:
                return SoilData.objects.create(parcel=parcel, data=last_data)

        return soil_data_obj  # jamais arrivé sauf si aucun point existant

    @staticmethod
    def fetch_climate(parcel: Parcel, start=None, end=None):
        climate_data_obj = ClimateData.objects.filter(parcel=parcel).order_by('-created_at').last()
        if climate_data_obj:
            return climate_data_obj

        point = ParcelDataService.get_first_point(parcel)
        lat, lon = point["lat"], point["lng"]
        start = start or timezone.now().strftime("%Y%m%d")
        end = end or (timezone.now() + timezone.timedelta(days=7)).strftime("%Y%m%d")

        url = (
            f"https://power.larc.nasa.gov/api/temporal/daily/point?"
            f"parameters=T2M,PRECTOTCORR&community=AG&longitude={lon}&latitude={lat}"
            f"&start={start}&end={end}&format=JSON"
        )
        resp = requests.get(url)
        if resp.status_code == 200:
            return ClimateData.objects.create(parcel=parcel, data=resp.json(), start=start, end=end)
        return None

    @staticmethod
    @lru_cache(maxsize=128)
    def build_parcel_crops(parcel):
        parcel_crops_info = []
        for pc in parcel.parcel_crops.all():
            tasks_info = [
                {
                    "id": task.id,
                    "name": task.name,
                    "status": task.status.name if task.status else None,
                    "due_date": task.due_date,
                    "priority": task.priority.name if task.priority else None,
                    "completed_at": task.completed_at
                }
                for task in pc.task_set.all()  # Relation Task → ParcelCrop
            ]
            parcel_crops_info.append({
                "parcel_crop_id": pc.id,
                "crop": {
                    "id": pc.crop.id,
                    "name": pc.crop.name,
                    "variety": pc.crop.variety.name if pc.crop.variety else None
                },
                "planting_date": pc.planting_date,
                "harvest_date": pc.harvest_date,
                "area": pc.area,
                "status": pc.status.name if pc.status else None,
                "tasks": tasks_info
            })
        return parcel_crops_info

    @staticmethod
    @lru_cache(maxsize=128)
    def build_yield_records(parcel):
        yield_records = []
        for pc in parcel.parcel_crops.all():
            pc_yields = YieldRecord.objects.filter(parcelCrop=pc)
            for yr in pc_yields:
                yield_records.append({
                    "parcel_crop_id": pc.id,
                    "date": yr.date,
                    "yield": yr.yield_amount,
                    "notes": yr.notes
                })
        return yield_records
