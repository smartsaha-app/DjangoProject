from functools import lru_cache
import requests
from django.utils import timezone
from SmartSaha.models import Parcel, SoilData, WeatherData, YieldRecord, Task


class ParcelDataService:

    @staticmethod
    def get_first_point(parcel: Parcel):
        if not parcel.points or len(parcel.points) == 0:
            raise ValueError("Parcel has no points")
        return parcel.points[0]


    @staticmethod
    def fetch_soil(parcel: Parcel, force_refresh=False):
        """
        Récupère les données sol avec gestion des valeurs null et cache intelligent
        """
        # Vérifier si on a des données récentes (30 jours) et non-null
        if not force_refresh:
            recent_soil = SoilData.objects.filter(
                parcel=parcel,
                created_at__gte=timezone.now() - timezone.timedelta(days=30)
            ).order_by('-created_at').first()

            if recent_soil and ParcelDataService.has_valid_soil_data(recent_soil):
                print("✅ Utilisation des données sol existantes valides")
                return recent_soil

        # Si données inexistantes, nulles ou forcées, appeler l'API
        print("🔄 Appel API SoilGrids pour nouvelles données...")
        point = ParcelDataService.get_first_point(parcel)
        lat, lon = point["lat"], point["lng"]

        url = (
            f"https://rest.isric.org/soilgrids/v2.0/properties/query?"
            f"lon={lon}&lat={lat}&property=phh2o&property=soc&property=nitrogen"
            f"&property=sand&property=clay&property=silt&depth=0-5cm&value=mean"
        )

        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                soil_data = resp.json()

                # Vérifier si les données sont valides (pas toutes null)
                if ParcelDataService.is_soil_data_valid(soil_data):
                    return SoilData.objects.create(parcel=parcel, data=soil_data)
                else:
                    print("⚠️ Données sol invalides (toutes null), utilisation des valeurs par défaut")
                    return ParcelDataService.create_default_soil_data(parcel, lat, lon)
            else:
                print(f"❌ Erreur API SoilGrids: {resp.status_code}")
                return ParcelDataService.get_fallback_soil_data(parcel)

        except requests.exceptions.Timeout:
            print("❌ Timeout API SoilGrids")
            return ParcelDataService.get_fallback_soil_data(parcel)
        except Exception as e:
            print(f"❌ Erreur API SoilGrids: {str(e)}")
            return ParcelDataService.get_fallback_soil_data(parcel)

    @staticmethod
    def has_valid_soil_data(soil_data_obj):
        """Vérifie si les données sol contiennent des valeurs non-null"""
        if not soil_data_obj or not soil_data_obj.data:
            return False

        layers = soil_data_obj.data.get('properties', {}).get('layers', [])
        for layer in layers:
            depths = layer.get('depths', [])
            for depth in depths:
                mean_value = depth.get('values', {}).get('mean')
                if mean_value is not None:
                    return True
        return False

    @staticmethod
    def is_soil_data_valid(soil_data):
        """Vérifie si les nouvelles données de l'API sont valides"""
        if not soil_data:
            return False

        layers = soil_data.get('properties', {}).get('layers', [])
        valid_layers = 0

        for layer in layers:
            depths = layer.get('depths', [])
            for depth in depths:
                mean_value = depth.get('values', {}).get('mean')
                if mean_value is not None:
                    valid_layers += 1
                    break  # Au moins une valeur non-null dans cette couche

        # Considérer valide si au moins 50% des couches ont des données
        return valid_layers >= len(layers) * 0.5

    @staticmethod
    def create_default_soil_data(parcel, lat, lon):
        """Crée des données sol par défaut basées sur la région"""
        # Valeurs par défaut pour Madagascar (à adapter selon votre région)
        default_data = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [lon, lat]
            },
            "properties": {
                "layers": [
                    {
                        "name": "clay",
                        "depths": [{"label": "0-5cm", "range": {"top_depth": 0, "bottom_depth": 5},
                                    "values": {"mean": 25.0}}],
                        "unit_measure": {"d_factor": 10, "mapped_units": "g/kg", "target_units": "%"}
                    },
                    {
                        "name": "nitrogen",
                        "depths": [{"label": "0-5cm", "range": {"top_depth": 0, "bottom_depth": 5},
                                    "values": {"mean": 1.2}}],
                        "unit_measure": {"d_factor": 100, "mapped_units": "cg/kg", "target_units": "g/kg"}
                    },
                    {
                        "name": "phh2o",
                        "depths": [{"label": "0-5cm", "range": {"top_depth": 0, "bottom_depth": 5},
                                    "values": {"mean": 6.5}}],
                        "unit_measure": {"d_factor": 10, "mapped_units": "pH*10", "target_units": "-"}
                    },
                    {
                        "name": "sand",
                        "depths": [{"label": "0-5cm", "range": {"top_depth": 0, "bottom_depth": 5},
                                    "values": {"mean": 40.0}}],
                        "unit_measure": {"d_factor": 10, "mapped_units": "g/kg", "target_units": "%"}
                    },
                    {
                        "name": "silt",
                        "depths": [{"label": "0-5cm", "range": {"top_depth": 0, "bottom_depth": 5},
                                    "values": {"mean": 35.0}}],
                        "unit_measure": {"d_factor": 10, "mapped_units": "g/kg", "target_units": "%"}
                    },
                    {
                        "name": "soc",
                        "depths": [{"label": "0-5cm", "range": {"top_depth": 0, "bottom_depth": 5},
                                    "values": {"mean": 2.0}}],
                        "unit_measure": {"d_factor": 10, "mapped_units": "dg/kg", "target_units": "g/kg"}
                    }
                ]
            },
            "metadata": {
                "source": "default_values",
                "region": "Madagascar",
                "notes": "Valeurs par défaut pour sols tropicaux"
            }
        }

        return SoilData.objects.create(parcel=parcel, data=default_data)

    @staticmethod
    def get_fallback_soil_data(parcel):
        """Récupère les meilleures données disponibles en fallback"""
        # Chercher n'importe quelle donnée sol existante pour cette parcelle
        existing_soil = SoilData.objects.filter(parcel=parcel).order_by('-created_at').first()
        if existing_soil:
            print("⚠️ Utilisation des données sol existantes (fallback)")
            return existing_soil
        else:
            # Créer des données par défaut
            point = ParcelDataService.get_first_point(parcel)
            lat, lon = point["lat"], point["lng"]
            print("⚠️ Création de données sol par défaut (fallback)")
            return ParcelDataService.create_default_soil_data(parcel, lat, lon)

    @staticmethod
    def refresh_soil_data(parcel: Parcel):
        """Force le rafraîchissement des données sol"""
        return ParcelDataService.fetch_soil(parcel, force_refresh=True)

    @staticmethod
    def fetch_weather(parcel: Parcel, required_days=3):
        """Version qui vérifie si les données existantes ont assez de jours"""

        # Vérifier d'abord si on a des données récentes ET avec assez de jours
        recent_weather = WeatherData.objects.filter(
            parcel=parcel,
            created_at__gte=timezone.now() - timezone.timedelta(hours=24)
        ).order_by('-created_at').first()

        # Vérifier si les données existantes ont assez de jours
        if recent_weather and ParcelDataService.has_enough_forecast_days(recent_weather, required_days):
            print(
                f"✅ Utilisation des données existantes ({ParcelDataService.get_forecast_days_count(recent_weather)} jours)")
            return recent_weather

        # Si pas de données récentes ou pas assez de jours, appeler l'API
        print("🔄 Appel API pour nouvelles données météo...")
        from SmartSaha.services import WeatherDataCollector
        collector = WeatherDataCollector()
        result = collector.collect_and_save_weather_data(
            parcel,
            forecast_days=required_days,
            include_hourly=False
        )

        if result['success']:
            actual_days = ParcelDataService.get_forecast_days_count(result['weather_data'])
            print(f"✅ Nouvelles données reçues ({actual_days} jours)")
            return result['weather_data']
        else:
            # Fallback sur les données existantes même si incomplètes
            print(f"⚠️ Erreur API, utilisation des données existantes: {result['error']}")
            return recent_weather or WeatherData.objects.create(
                parcel=parcel,
                data={'error': result['error']},
                start=timezone.now().date(),
                end=timezone.now().date() + timezone.timedelta(days=required_days - 1),
                location_name="Erreur de collecte",
                data_type='FORECAST',
                risk_level='LOW'
            )

    @staticmethod
    def has_enough_forecast_days(weather_data, required_days=3):
        """Vérifie si les données météo ont assez de jours de prévision"""
        if not weather_data or not weather_data.data:
            return False

        forecast_days = weather_data.data.get('forecast', {}).get('forecastday', [])
        return len(forecast_days) >= required_days

    @staticmethod
    def get_forecast_days_count(weather_data):
        """Retourne le nombre de jours de prévision disponibles"""
        if not weather_data or not weather_data.data:
            return 0
        forecast_days = weather_data.data.get('forecast', {}).get('forecastday', [])
        return len(forecast_days)

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
    def build_parcel_tasks(parcel):
        """Récupère toutes les tâches de la parcelle avec statistiques"""
        tasks = Task.objects.filter(parcelCrop__parcel=parcel).select_related(
            'parcelCrop', 'status', 'priority'
        ).order_by('due_date')

        tasks_info = []
        for task in tasks:
            tasks_info.append({
                "id": task.id,
                "name": task.name,
                "description": task.description,
                "due_date": task.due_date,
                "completed_at": task.completed_at,
                "created_at": task.created_at,
                "updated_at": task.updated_at,
                "status": {
                    "id": task.status.id if task.status else None,
                    "name": task.status.name if task.status else None
                },
                "priority": {
                    "id": task.priority.id if task.priority else None,
                    "name": task.priority.name if task.priority else None
                },
                "parcel_crop": {
                    "id": task.parcelCrop.id,
                    "crop_name": task.parcelCrop.crop.name if task.parcelCrop.crop else None,
                    "parcel_name": parcel.parcel_name
                }
            })

        # Statistiques des tâches
        task_stats = {
            "total": tasks.count(),
            "completed": tasks.filter(completed_at__isnull=False).count(),
            "pending": tasks.filter(completed_at__isnull=True).count(),
            "overdue": tasks.filter(
                completed_at__isnull=True,
                due_date__lt=timezone.now().date()
            ).count(),
            "by_priority": {
                "HIGH": tasks.filter(priority__name="HIGH").count(),
                "MEDIUM": tasks.filter(priority__name="MEDIUM").count(),
                "LOW": tasks.filter(priority__name="LOW").count()
            }
        }

        return {
            "tasks": tasks_info,
            "statistics": task_stats
        }

    @staticmethod
    def get_tasks_summary(parcel):
        """Version résumée des tâches pour le dashboard"""
        tasks = Task.objects.filter(parcelCrop__parcel=parcel)

        # Tâches urgentes (échéance dans les 3 jours)
        urgent_tasks = tasks.filter(
            completed_at__isnull=True,
            due_date__lte=timezone.now().date() + timezone.timedelta(days=3)
        ).select_related('parcelCrop', 'priority').order_by('due_date')[:5]

        urgent_tasks_list = []
        for task in urgent_tasks:
            urgent_tasks_list.append({
                "id": task.id,
                "name": task.name,
                "due_date": task.due_date,
                "priority": task.priority.name if task.priority else None,
                "crop_name": task.parcelCrop.crop.name if task.parcelCrop.crop else None,
                "is_overdue": task.due_date < timezone.now().date()
            })

        return {
            "urgent_tasks": urgent_tasks_list,
            "total_pending": tasks.filter(completed_at__isnull=True).count(),
            "total_overdue": tasks.filter(
                completed_at__isnull=True,
                due_date__lt=timezone.now().date()
            ).count()
        }

    @staticmethod
    def get_complete_parcel_data(parcel_uuid: str):
        """Récupère toutes les données d'une parcelle (sol + météo + cultures + tâches)"""
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
                'yield_records': ParcelDataService.build_yield_records(parcel),
                'tasks': ParcelDataService.build_parcel_tasks(parcel),  # NOUVEAU
                'tasks_summary': ParcelDataService.get_tasks_summary(parcel)  # NOUVEAU
            }
        except Parcel.DoesNotExist:
            return None

    @staticmethod
    def get_user_parcels_tasks(user):
        """Récupère toutes les tâches de toutes les parcelles d'un utilisateur"""
        parcels = Parcel.objects.filter(owner=user)
        all_tasks = []

        for parcel in parcels:
            parcel_tasks = ParcelDataService.build_parcel_tasks(parcel)
            if parcel_tasks["tasks"]:
                all_tasks.append({
                    "parcel_name": parcel.parcel_name,
                    "parcel_uuid": str(parcel.uuid),
                    "tasks": parcel_tasks["tasks"],
                    "statistics": parcel_tasks["statistics"]
                })

        return all_tasks

    @staticmethod
    def format_weather_for_agriculture(weather_data_dict):
        """Formate les données météo pour 8 jours (aujourd'hui + 7)"""
        if not weather_data_dict or 'weather_data' not in weather_data_dict:
            return None

        weather_obj = weather_data_dict['weather_data']
        if not weather_obj or not weather_obj.data:
            return None

        raw_data = weather_obj.data

        # Extraire les données pour 8 jours
        formatted_data = {
            'current': {
                'temperature': raw_data.get('current', {}).get('temp_c'),
                'humidity': raw_data.get('current', {}).get('humidity'),
                'precipitation': raw_data.get('current', {}).get('precip_mm'),
                'condition': raw_data.get('current', {}).get('condition', {}).get('text'),
                'wind_speed': raw_data.get('current', {}).get('wind_kph'),
                'feels_like': raw_data.get('current', {}).get('feelslike_c'),
                'pressure': raw_data.get('current', {}).get('pressure_mb'),
                'visibility': raw_data.get('current', {}).get('vis_km'),
                'uv_index': raw_data.get('current', {}).get('uv')
            },
            'daily_forecast': []
        }

        # Traiter les prévisions pour 8 jours (aujourd'hui inclus)
        forecast_days = raw_data.get('forecast', {}).get('forecastday', [])
        for day in forecast_days[:8]:  # Limiter à 8 jours maximum
            daily_data = day.get('day', {})
            formatted_data['daily_forecast'].append({
                'date': day.get('date'),
                'max_temp': daily_data.get('maxtemp_c'),
                'min_temp': daily_data.get('mintemp_c'),
                'avg_temp': daily_data.get('avgtemp_c'),
                'total_precip': daily_data.get('totalprecip_mm'),
                'chance_of_rain': daily_data.get('daily_chance_of_rain'),
                'condition': daily_data.get('condition', {}).get('text'),
                'uv_index': daily_data.get('uv'),
                'max_wind': daily_data.get('maxwind_kph'),
                'avg_humidity': daily_data.get('avghumidity'),
                'will_it_rain': daily_data.get('daily_will_it_rain'),
                'will_it_snow': daily_data.get('daily_will_it_snow')
            })

        return formatted_data

    @staticmethod
    def get_weather_summary_8_days(weather_data_dict):
        """Génère un résumé pour les 8 jours"""
        if not weather_data_dict:
            return None

        formatted_data = ParcelDataService.format_weather_for_agriculture(weather_data_dict)
        if not formatted_data:
            return None

        daily_forecast = formatted_data.get('daily_forecast', [])

        # Calculer les statistiques sur 8 jours
        max_temps = [day['max_temp'] for day in daily_forecast if day['max_temp'] is not None]
        min_temps = [day['min_temp'] for day in daily_forecast if day['min_temp'] is not None]
        total_rain = sum([day['total_precip'] or 0 for day in daily_forecast])
        rainy_days = sum([1 for day in daily_forecast if (day['chance_of_rain'] or 0) > 50])

        return {
            'current_conditions': formatted_data.get('current', {}),
            'forecast_stats': {
                'max_temp': max(max_temps) if max_temps else None,
                'min_temp': min(min_temps) if min_temps else None,
                'total_rain': round(total_rain, 1),
                'rainy_days': rainy_days,
                'forecast_period': f"{len(daily_forecast)} jours"
            },
            'period': '8_jours'  # Indiquer la période couverte
        }

    @staticmethod
    def serialize_weather_data(weather_data_dict):
        """Sérialise les données météo formatées pour 8 jours"""
        if not weather_data_dict:
            return None

        weather_obj = weather_data_dict['weather_data']
        formatted_weather = ParcelDataService.format_weather_for_agriculture(weather_data_dict)

        # Utiliser le nouveau résumé pour 8 jours
        summary = ParcelDataService.get_weather_summary_8_days(weather_data_dict)

        return {
            'data': formatted_weather,
            'analysis': weather_data_dict.get('analysis', {}),
            'alerts': weather_data_dict.get('alerts', []),
            'summary': summary,  # Nouveau résumé pour 8 jours
            'metadata': {
                'location_name': weather_obj.location_name if weather_obj else None,
                'data_type': weather_obj.data_type if weather_obj else None,
                'risk_level': weather_obj.risk_level if weather_obj else None,
                'start_date': weather_obj.start.isoformat() if weather_obj and weather_obj.start else None,
                'end_date': weather_obj.end.isoformat() if weather_obj and weather_obj.end else None,
                'created_at': weather_obj.created_at.isoformat() if weather_obj else None,
                'forecast_days': 8  # Indiquer explicitement le nombre de jours
            }
        }

    @staticmethod
    def serialize_soil_data(soil_data_obj):
        """Sérialise les données sol avec gestion des valeurs nulles"""
        if not soil_data_obj:
            return None

        data = soil_data_obj.data
        if not data:
            return None

        # Calculer le pourcentage de données valides
        layers = data.get('properties', {}).get('layers', [])
        valid_data_count = 0
        total_data_count = 0

        formatted_layers = []
        for layer in layers:
            layer_name = layer.get('name')
            depths = layer.get('depths', [])

            for depth in depths:
                mean_value = depth.get('values', {}).get('mean')
                total_data_count += 1
                if mean_value is not None:
                    valid_data_count += 1

            formatted_layers.append({
                "name": layer_name,
                "depths": depths,
                "unit_measure": layer.get('unit_measure', {})
            })

        validity_percentage = (valid_data_count / total_data_count * 100) if total_data_count > 0 else 0

        return {
            "data": {
                "type": data.get('type'),
                "geometry": data.get('geometry'),
                "properties": {
                    "layers": formatted_layers,
                    "data_quality": {
                        "valid_percentage": round(validity_percentage, 1),
                        "valid_count": valid_data_count,
                        "total_count": total_data_count,
                        "status": "good" if validity_percentage > 70 else "poor" if validity_percentage > 30 else "very_poor"
                    }
                },
                "query_time_s": data.get('query_time_s')
            },
            "metadata": {
                "created_at": soil_data_obj.created_at.isoformat(),
                "depth": "0-5cm",
                "source": data.get('metadata', {}).get('source', 'soilgrids_api'),
                "data_quality_note": ParcelDataService.get_soil_quality_note(validity_percentage)
            }
        }

    @staticmethod
    def get_soil_quality_note(validity_percentage):
        """Retourne une note sur la qualité des données"""
        if validity_percentage > 90:
            return "Données complètes et fiables"
        elif validity_percentage > 70:
            return "Données majoritairement disponibles"
        elif validity_percentage > 50:
            return "Données partiellement disponibles"
        elif validity_percentage > 30:
            return "Données limitées - valeurs par défaut utilisées"
        else:
            return "Données très limitées - estimations utilisées"