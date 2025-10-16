from django.core.cache import cache
from django.db.models import Sum, Avg, Count, F, Q
from SmartSaha.models import Parcel, ParcelCrop, YieldRecord, Task, SoilData, ClimateData

class DashboardService:
    """
    Dashboard optimisé : utilise des agrégations SQL pour rendements et tâches,
    précharge les relations pour sols et climat, et met en cache les blocs.
    """
    CACHE_TIMEOUT = 60 * 15  # 15 min

    def __init__(self, user):
        self.user = user

    # ---------------- Parcelles ----------------
    def get_parcels_data(self):
        cache_key = f"dashboard_{self.user.pk}_parcels"
        data = cache.get(cache_key)
        if data:
            return data

        parcels = Parcel.objects.filter(owner=self.user)
        data = [{"id": str(p.uuid), "name": p.parcel_name, "points": p.points} for p in parcels]
        cache.set(cache_key, data, timeout=self.CACHE_TIMEOUT)
        return data

    # ---------------- Sols ----------------
    def get_soil_summary(self):
        cache_key = f"dashboard_{self.user.pk}_soil"
        data = cache.get(cache_key)
        if data:
            return data

        parcels = Parcel.objects.filter(owner=self.user).prefetch_related("soildata_set")
        soil_summary = []

        for parcel in parcels:
            layer_agg = {}
            for soil in parcel.soildata_set.all():
                layers = soil.data.get("properties", {}).get("layers", [])
                for layer in layers:
                    name = layer.get("name")
                    for depth in layer.get("depths", []):
                        val = depth.get("values", {}).get("mean")
                        if val is not None:
                            layer_agg.setdefault(name, []).append(val)
            summary = {k: sum(v)/len(v) if v else None for k, v in layer_agg.items()} if layer_agg else None
            soil_summary.append({"parcel_id": str(parcel.uuid), "soil_summary": summary})

        cache.set(cache_key, soil_summary, timeout=self.CACHE_TIMEOUT)
        return soil_summary

    # ---------------- Climat ----------------
    def get_climate_summary(self):
        cache_key = f"dashboard_{self.user.pk}_climate"
        data = cache.get(cache_key)
        if data:
            return data

        parcels = Parcel.objects.filter(owner=self.user).prefetch_related("climatedata_set")
        climate_summary = []

        for parcel in parcels:
            t2m_values = []
            prectot_values = []
            for climate in parcel.climatedata_set.all():
                params = climate.data.get("properties", {}).get("parameter", {})
                for v in params.get("T2M", {}).values():
                    if isinstance(v, (int, float)) and v != -999:
                        t2m_values.append(v)
                for v in params.get("PRECTOTCORR", {}).values():
                    if isinstance(v, (int, float)) and v != -999:
                        prectot_values.append(v)

            summary = {
                "avg_temperature": sum(t2m_values)/len(t2m_values) if t2m_values else None,
                "total_precipitation": sum(prectot_values) if prectot_values else None
            } if t2m_values or prectot_values else None

            climate_summary.append({"parcel_id": str(parcel.uuid), "climate_summary": summary})

        cache.set(cache_key, climate_summary, timeout=self.CACHE_TIMEOUT)
        return climate_summary

    # ---------------- Rendements ----------------
    def get_yield_summary(self):
        cache_key = f"dashboard_{self.user.pk}_yield"
        data = cache.get(cache_key)
        if data:
            return data

        # Agrégation SQL : sum et avg par ParcelCrop
        parcel_crops = (
            ParcelCrop.objects.filter(parcel__owner=self.user)
            .annotate(
                total_yield=Sum("yieldrecord__yield_amount"),
                avg_yield=Avg("yieldrecord__yield_amount"),
                parcel_name=F("parcel__parcel_name"),
                crop_name=F("crop__name")
            )
        )

        data = [
            {
                "parcel_crop_id": pc.id,
                "parcel_name": pc.parcel_name,
                "crop_name": pc.crop_name,
                "summary": {
                    "total_yield": pc.total_yield,
                    "avg_yield": pc.avg_yield
                } if pc.total_yield is not None else None
            } for pc in parcel_crops
        ]

        cache.set(cache_key, data, timeout=self.CACHE_TIMEOUT)
        return data

    # ---------------- Tâches ----------------
    def get_task_summary(self):
        cache_key = f"dashboard_{self.user.pk}_task"
        data = cache.get(cache_key)
        if data:
            return data

        # Agrégation SQL : total et complétées par Parcel
        parcels = Parcel.objects.filter(owner=self.user)
        data = []
        for parcel in parcels:
            tasks = Task.objects.filter(parcelCrop__parcel=parcel)
            agg = tasks.aggregate(
                total_tasks=Count("id"),
                completed_tasks=Count("id", filter=Q(status__name="Done"))
            )
            data.append({
                "parcel_id": str(parcel.uuid),
                "task_summary": {
                    "total_tasks": agg.get("total_tasks", 0),
                    "completed_tasks": agg.get("completed_tasks", 0)
                }
            })

        cache.set(cache_key, data, timeout=self.CACHE_TIMEOUT)
        return data

    # ---------------- Dashboard complet ----------------
    def get_full_dashboard(self):
        """
        Assemble les blocs depuis le cache (ou calcule si cache vide)
        """
        return {
            "parcels": self.get_parcels_data(),
            "soil_summary": self.get_soil_summary(),
            "climate_summary": self.get_climate_summary(),
            "yield_summary": self.get_yield_summary(),
            "task_summary": self.get_task_summary(),
        }
