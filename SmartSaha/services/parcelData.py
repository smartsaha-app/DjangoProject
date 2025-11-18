from functools import lru_cache
import requests
from django.utils import timezone
from SmartSaha.models import Parcel, SoilData, WeatherData, YieldRecord


class ParcelDataService:

    @staticmethod
    def get_first_point(parcel: Parcel):
        if not parcel.points or len(parcel.points) == 0:
            raise ValueError("Parcel has no points")
        return parcel.points[0]

    @staticmethod
    def fetch_soil(parcel: Parcel):
        soil_data_obj = SoilData.objects.filter(parcel=parcel).order_by('-created_at').last()
        if soil_data_obj:
            return soil_data_obj

        point = ParcelDataService.get_first_point(parcel)
        lat, lon = point["lat"], point["lng"]
        url = (
            f"https://rest.isric.org/soilgrids/v2.0/properties/query?"
            f"lon={lon}&lat={lat}&property=phh2o&property=soc&property=nitrogen"
            f"&property=sand&property=clay&property=silt&depth=0-5cm&value=mean"
        )
        resp = requests.get(url)
        if resp.status_code == 200:
            return SoilData.objects.create(parcel=parcel, data=resp.json())
        return None

    @staticmethod
    def fetch_weather(parcel: Parcel):
        """Remplacer ClimateData par WeatherData avec le nouveau système"""
        # Vérifier d'abord si on a des données récentes (moins de 24h)
        recent_weather = WeatherData.objects.filter(
            parcel=parcel,
            created_at__gte=timezone.now() - timezone.timedelta(hours=24)
        ).order_by('-created_at').first()

        if recent_weather:
            return recent_weather

        # Si pas de données récentes, utiliser le nouveau collecteur
        from SmartSaha.services import WeatherDataCollector  # Import du nouveau service
        collector = WeatherDataCollector()
        result = collector.collect_and_save_weather_data(parcel)

        if result['success']:
            return result['weather_data']
        else:
            # Fallback : créer un WeatherData minimal avec message d'erreur
            return WeatherData.objects.create(
                parcel=parcel,
                data={'error': result['error']},
                start=timezone.now().date(),
                end=timezone.now().date() + timezone.timedelta(days=1),
                location_name="Erreur de collecte",
                data_type='CURRENT',
                risk_level='LOW'
            )

    @staticmethod
    def get_weather_analysis(parcel: Parcel):
        """Récupère l'analyse météo complète pour une parcelle"""
        weather_data = ParcelDataService.fetch_weather(parcel)

        if not weather_data:
            return None

        # Utiliser le nouvel analyseur agricole
        from SmartSaha.services import AgriculturalAnalyzer
        analyzer = AgriculturalAnalyzer()

        return {
            'weather_data': weather_data,
            'analysis': analyzer.analyze_weather_data(weather_data),
            'alerts': weather_data.agricultural_alerts,
            'summary': weather_data.get_weather_summary()
        }

    @staticmethod
    # @lru_cache(maxsize=128)
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
    # @lru_cache(maxsize=128)
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

    @staticmethod
    def get_complete_parcel_data(parcel_uuid: str):
        """Récupère toutes les données d'une parcelle (sol + météo + cultures)"""
        try:
            parcel = Parcel.objects.get(uuid=parcel_uuid)

            return {
                'parcel': {
                    'uuid': str(parcel.uuid),
                    'name': parcel.parcel_name,
                    'points': parcel.points,
                    'created_at': parcel.created_at
                },
                'soil_data': ParcelDataService.fetch_soil(parcel),
                'weather_data': ParcelDataService.get_weather_analysis(parcel),
                'crops': ParcelDataService.build_parcel_crops(parcel),
                'yield_records': ParcelDataService.build_yield_records(parcel)
            }
        except Parcel.DoesNotExist:
            return None