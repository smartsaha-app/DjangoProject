from django.db.models import Sum, Count
from SmartSaha.models import (Parcel, ParcelCrop, YieldRecord, Task,
                              # CarbonRecord,
                              SoilData, ClimateData)

class DashboardService:
    """
    Service orienté objet pour construire les données du Dashboard BI
    en extrayant correctement les JSON de sols et météo.
    """

    def __init__(self, user):
        self.user = user
        self.parcels = Parcel.objects.filter(owner=self.user)
        self.parcel_crops = ParcelCrop.objects.filter(parcel__in=self.parcels)

    # ---------------- Parcelles ----------------
    def get_parcels_data(self):
        return [
            {"id": str(parcel.uuid), "name": parcel.parcel_name, "points": parcel.points}
            for parcel in self.parcels
        ]

    # ---------------- Sols ----------------
    def get_soil_summary(self):
        soil_summary = []
        for parcel in self.parcels:
            soils = SoilData.objects.filter(parcel=parcel)
            if soils.exists():
                # Moyenne par couche
                layer_agg = {}
                for soil in soils:
                    layers = soil.data.get("properties", {}).get("layers", [])
                    for layer in layers:
                        name = layer.get("name")
                        for depth in layer.get("depths", []):
                            mean_val = depth.get("values", {}).get("mean")
                            if mean_val is not None:
                                layer_agg.setdefault(name, []).append(mean_val)
                # Calcul de la moyenne
                summary = {k: sum(v)/len(v) if v else None for k, v in layer_agg.items()}
            else:
                summary = None
            soil_summary.append({"parcel_id": str(parcel.uuid), "soil_summary": summary})
        return soil_summary

    # ---------------- Climat ----------------
    def get_climate_summary(self):
        climate_summary = []
        for parcel in self.parcels:
            climates = ClimateData.objects.filter(parcel=parcel)
            t2m_values = []
            prectot_values = []

            for climate in climates:
                data_param = climate.data.get("properties", {}).get("parameter", {})

                # Récupération des températures
                t2m_dict = data_param.get("T2M", {})
                for date, value in t2m_dict.items():
                    if isinstance(value, (int, float)) and value != -999:
                        t2m_values.append(value)

                # Récupération des précipitations
                prectot_dict = data_param.get("PRECTOTCORR", {})
                for date, value in prectot_dict.items():
                    if isinstance(value, (int, float)) and value != -999:
                        prectot_values.append(value)

            summary = {
                "avg_temperature": sum(t2m_values) / len(t2m_values) if t2m_values else None,
                "total_precipitation": sum(prectot_values) if prectot_values else None
            } if t2m_values or prectot_values else None

            climate_summary.append({"parcel_id": str(parcel.uuid), "climate_summary": summary})

        return climate_summary

    # ---------------- Rendements ----------------
    def get_yield_summary(self):
        yield_summary = []
        for parcel in self.parcels:
            for pc in parcel.parcel_crops.all():
                yields = YieldRecord.objects.filter(parcelCrop=pc)
                if yields.exists():
                    total = sum([y.yield_amount for y in yields])
                    avg = total / yields.count()
                    summary = {"total_yield": total, "avg_yield": avg}
                else:
                    summary = None
                yield_summary.append({
                    "parcel_crop_id": pc.id,
                    "parcel_name": parcel.parcel_name,
                    "crop_name": pc.crop.name,
                    "summary": summary
                })
        return yield_summary

    # ---------------- Tâches ----------------
    def get_task_summary(self):
        task_summary = []
        for parcel in self.parcels:
            total_tasks = 0
            completed_tasks = 0

            for pc in parcel.parcel_crops.all():
                tasks = pc.task_set.all()  # toutes les tâches liées à ce ParcelCrop
                total_tasks += tasks.count()
                completed_tasks += tasks.filter(status__name="Done").count()

            summary = {
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks
            }
            task_summary.append({"parcel_id": str(parcel.uuid), "task_summary": summary})
        return task_summary

    # ---------------- Carbone ----------------
    # def get_carbon_summary(self):
    #     carbon_summary = []
    #     for parcel in self.parcels:
    #         carbons = CarbonRecord.objects.filter(parcel=parcel)
    #         if carbons.exists():
    #             avg_carbon = sum([c.carbon_amount for c in carbons]) / carbons.count()
    #         else:
    #             avg_carbon = None
    #         carbon_summary.append({"parcel_id": str(parcel.uuid), "carbon_summary": {"avg_carbon": avg_carbon}})
    #     return carbon_summary

    # ---------------- Dashboard complet ----------------
    def get_full_dashboard(self):
        return {
            "parcels": self.get_parcels_data(),
            "soil_summary": self.get_soil_summary(),
            "climate_summary": self.get_climate_summary(),
            "yield_summary": self.get_yield_summary(),
            "task_summary": self.get_task_summary(),
            # "carbon_summary": self.get_carbon_summary()
        }
