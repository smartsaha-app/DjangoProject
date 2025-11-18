from django.core.cache import cache
from django.db.models import Sum, Avg, Count, F, Q
from SmartSaha.models import Parcel, ParcelCrop, YieldRecord, Task, SoilData, ClimateData, WeatherData


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

    # ---------------- Météo ----------------
    def get_weather_summary(self):
        cache_key = f"dashboard_{self.user.pk}_weather"
        data = cache.get(cache_key)
        if data:
            return data

        parcels = Parcel.objects.filter(owner=self.user).prefetch_related("weatherdata_set")
        weather_summary = []

        for parcel in parcels:
            # Récupérer les données météo les plus récentes
            latest_weather = parcel.weatherdata_set.order_by('-created_at').first()

            if latest_weather:
                # Utiliser les propriétés calculées de WeatherData
                summary = {
                    "current_temperature": latest_weather.current_temperature,
                    "total_precipitation": latest_weather.total_precipitation,
                    "risk_level": latest_weather.risk_level,
                    "location": latest_weather.location_name,
                    "alerts_count": len(latest_weather.agricultural_alerts),
                    "optimal_planting_days": latest_weather.optimal_planting_days,
                    "irrigation_recommendation": latest_weather.irrigation_recommendation,
                    "weather_summary": latest_weather.get_weather_summary()
                }
            else:
                summary = None

            weather_summary.append({
                "parcel_id": str(parcel.uuid),
                "parcel_name": parcel.parcel_name,
                "weather_summary": summary
            })

        cache.set(cache_key, weather_summary, timeout=self.CACHE_TIMEOUT)
        return weather_summary

    def get_enhanced_weather_summary(self):
        """Version enrichie avec analyse agricole complète"""
        cache_key = f"dashboard_{self.user.pk}_enhanced_weather"
        data = cache.get(cache_key)
        if data:
            return data

        parcels = Parcel.objects.filter(owner=self.user).prefetch_related("weatherdata_set")
        enhanced_summary = []

        for parcel in parcels:
            latest_weather = parcel.weatherdata_set.order_by('-created_at').first()

            if latest_weather:
                # Utiliser l'analyseur agricole pour des insights avancés
                from SmartSaha.services import AgriculturalAnalyzer
                analyzer = AgriculturalAnalyzer()
                analysis = analyzer.analyze_weather_data(latest_weather)

                summary = {
                    # Données de base
                    "current_temperature": latest_weather.current_temperature,
                    "total_precipitation": latest_weather.total_precipitation,
                    "risk_level": latest_weather.risk_level,
                    "location": latest_weather.location_name,

                    # Alertes et risques
                    "alerts": latest_weather.agricultural_alerts,
                    "high_priority_alerts": [a for a in latest_weather.agricultural_alerts if a['severity'] == 'HIGH'],
                    "risk_assessment": analysis['risk_assessment'],

                    # Recommandations agricoles
                    "optimal_planting_days": analysis['optimal_planting_days'],
                    "irrigation_recommendation": analysis['irrigation_recommendation'],
                    "growing_degree_days": latest_weather.calculate_growing_degree_days(),

                    # Résumé météo
                    "weather_conditions": latest_weather.get_weather_summary(),
                    "data_type": latest_weather.data_type,
                    "last_updated": latest_weather.created_at
                }
            else:
                summary = {
                    "status": "no_data",
                    "message": "Aucune donnée météo disponible"
                }

            enhanced_summary.append({
                "parcel_id": str(parcel.uuid),
                "parcel_name": parcel.parcel_name,
                "weather_data": summary
            })

        cache.set(cache_key, enhanced_summary, timeout=self.CACHE_TIMEOUT)
        return enhanced_summary

    def get_dashboard_weather_overview(self):
        """Version compacte pour le dashboard principal"""
        cache_key = f"dashboard_{self.user.pk}_weather_overview"
        data = cache.get(cache_key)
        if data:
            return data

        parcels = Parcel.objects.filter(owner=self.user)
        overview = {
            "total_parcels": parcels.count(),
            "parcels_with_weather_data": 0,
            "high_risk_parcels": 0,
            "total_alerts": 0,
            "parcel_details": []
        }

        for parcel in parcels:
            latest_weather = WeatherData.objects.filter(parcel=parcel).order_by('-created_at').first()

            if latest_weather:
                overview["parcels_with_weather_data"] += 1

                alerts = latest_weather.agricultural_alerts
                high_risk_alerts = [a for a in alerts if a['severity'] == 'HIGH']

                if latest_weather.risk_level == 'HIGH' or len(high_risk_alerts) > 0:
                    overview["high_risk_parcels"] += 1

                overview["total_alerts"] += len(alerts)

                parcel_info = {
                    "parcel_id": str(parcel.uuid),
                    "parcel_name": parcel.parcel_name,
                    "current_temperature": latest_weather.current_temperature,
                    "risk_level": latest_weather.risk_level,
                    "alerts_count": len(alerts),
                    "high_priority_alerts": len(high_risk_alerts),
                    "location": latest_weather.location_name
                }
            else:
                parcel_info = {
                    "parcel_id": str(parcel.uuid),
                    "parcel_name": parcel.parcel_name,
                    "status": "no_data"
                }

            overview["parcel_details"].append(parcel_info)

        cache.set(cache_key, overview, timeout=self.CACHE_TIMEOUT)
        return overview

    def refresh_weather_data(self):
        """Force le rafraîchissement des données météo pour toutes les parcelles"""
        from SmartSaha.services import WeatherDataCollector

        collector = WeatherDataCollector()
        parcels = Parcel.objects.filter(owner=self.user)

        refresh_results = []

        for parcel in parcels:
            if parcel.points:  # Vérifier que la parcelle a des coordonnées
                result = collector.collect_and_save_weather_data(parcel)
                refresh_results.append({
                    "parcel_name": parcel.parcel_name,
                    "success": result['success'],
                    "alerts_generated": result.get('alerts_generated', 0),
                    "error": result.get('error')
                })

        # Nettoyer le cache
        cache_keys = [
            f"dashboard_{self.user.pk}_weather",
            f"dashboard_{self.user.pk}_enhanced_weather",
            f"dashboard_{self.user.pk}_weather_overview"
        ]
        for key in cache_keys:
            cache.delete(key)

        return refresh_results
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
            "climate_summary": self.get_dashboard_weather_overview(),
            "yield_summary": self.get_yield_summary(),
            "task_summary": self.get_task_summary(),
        }
