# SmartSaha/services/weather_service.py
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from django.utils import timezone


class WeatherDataService:
    """Service concret pour la gestion des données météo"""

    def process_weather_data(self, raw_data: Dict, parcel) -> Dict:
        """Traite les données météo brutes et crée l'objet WeatherData"""

        # Extraction des métadonnées
        metadata = self._extract_metadata(raw_data)

        # Création de l'objet WeatherData
        weather_data = self._create_weather_data(parcel, raw_data, metadata)

        # Génération des alertes
        alerts_count = self._generate_agricultural_alerts(weather_data)

        return {
            'weather_data': weather_data,
            'alerts_count': alerts_count,
            'risk_level': metadata['risk_level']
        }

    def _extract_metadata(self, raw_data: Dict) -> Dict:
        """Extrait les métadonnées importantes du JSON brut"""
        location = raw_data.get('location', {})
        current = raw_data.get('current', {})

        return {
            'location_name': location.get('name', ''),
            'data_type': 'FORECAST',
            'risk_level': self._calculate_risk_level(raw_data),
            'start_date': timezone.now().date(),
            'end_date': self._calculate_end_date(raw_data)
        }

    def _calculate_risk_level(self, weather_data: Dict) -> str:
        """Calcule le niveau de risque basé sur les prévisions"""
        forecast_days = weather_data.get('forecast', {}).get('forecastday', [])

        high_risk_days = 0
        for day in forecast_days:
            day_data = day['day']
            if (day_data['totalprecip_mm'] > 20 or
                    day_data['mintemp_c'] < 5 or
                    (day_data['totalprecip_mm'] == 0 and day_data['avgtemp_c'] > 30)):
                high_risk_days += 1

        if high_risk_days >= 2:
            return 'HIGH'
        elif high_risk_days >= 1:
            return 'MEDIUM'
        else:
            return 'LOW'

    def _calculate_end_date(self, weather_data: Dict):
        """Calcule la date de fin basée sur les prévisions"""
        forecast_days = weather_data.get('forecast', {}).get('forecastday', [])
        if forecast_days:
            last_day = forecast_days[-1]['date']
            return datetime.strptime(last_day, '%Y-%m-%d').date()
        return timezone.now().date() + timedelta(days=1)

    def _create_weather_data(self, parcel, raw_data: Dict, metadata: Dict):
        """Crée et sauvegarde l'objet WeatherData"""
        from SmartSaha.models import WeatherData

        return WeatherData.objects.create(
            parcel=parcel,
            data=raw_data,
            start=metadata['start_date'],
            end=metadata['end_date'],
            location_name=metadata['location_name'],
            data_type=metadata['data_type'],
            risk_level=metadata['risk_level']
        )

    def _generate_agricultural_alerts(self, weather_data) -> int:
        """Génère et sauvegarde les alertes agricoles"""
        from SmartSaha.models import AgriculturalAlert

        alerts_data = weather_data.agricultural_alerts
        alerts_created = 0

        for alert_data in alerts_data:
            AgriculturalAlert.objects.create(
                weather_data=weather_data,
                alert_type=alert_data['type'],
                message=alert_data['message'],
                recommendation=alert_data.get('action', ''),
                severity=alert_data['severity'],
                alert_date=alert_data['date']
            )
            alerts_created += 1

        return alerts_created


class AgriculturalAnalyzer:
    """Analyseur agricole concret"""

    def __init__(self):
        self.risk_thresholds = {
            'heavy_rain': 20.0,
            'frost': 5.0,
            'drought': {'precip': 0.0, 'temp': 30.0},
            'strong_wind': 30.0,
            'high_humidity': 85.0
        }

    def analyze_weather_data(self, weather_data) -> Dict:
        """Analyse complète des données météo pour l'SmartSaha"""
        return {
            'alerts': weather_data.agricultural_alerts,
            'optimal_planting_days': self._find_optimal_planting_days(weather_data),
            'irrigation_recommendation': self._calculate_irrigation_needs(weather_data),
            'risk_assessment': self._assess_overall_risk(weather_data)
        }

    def _find_optimal_planting_days(self, weather_data):
        """Trouve les jours optimaux pour les semis"""
        optimal_days = []
        forecast_days = weather_data.data.get('forecast', {}).get('forecastday', [])

        for day in forecast_days:
            day_data = day['day']
            if self._is_optimal_planting_day(day_data):
                optimal_days.append({
                    'date': day['date'],
                    'score': self._calculate_planting_score(day_data),
                    'conditions': {
                        'temperature': day_data['avgtemp_c'],
                        'precipitation': day_data['totalprecip_mm'],
                        'humidity': day_data['avghumidity']
                    }
                })

        return sorted(optimal_days, key=lambda x: x['score'], reverse=True)[:3]

    def _is_optimal_planting_day(self, day_data: Dict) -> bool:
        """Détermine si c'est un bon jour pour planter"""
        return (25 >= day_data['avgtemp_c'] >= 10 > day_data['totalprecip_mm'] and
                day_data['maxwind_kph'] < 25 and
                day_data['daily_chance_of_rain'] < 40)

    def _calculate_planting_score(self, day_data: Dict) -> int:
        """Calcule un score de pertinence pour la plantation"""
        score = 0

        # Température idéale = 20°C
        temp_diff = abs(day_data['avgtemp_c'] - 20)
        score += max(0, 30 - temp_diff * 3)

        # Peu de pluie = mieux
        score += max(0, 25 - day_data['totalprecip_mm'])

        # Vent modéré
        score += max(0, 20 - day_data['maxwind_kph'] / 2)

        return min(100, score)

    def _calculate_irrigation_needs(self, weather_data):
        """Calcule les besoins en irrigation"""
        total_rain = weather_data.total_precipitation

        if total_rain > 40:
            return {"action": "Aucune irrigation", "reason": "Pluies suffisantes"}
        elif total_rain > 20:
            return {"action": "Irrigation légère", "reason": "Pluies modérées"}
        else:
            return {"action": "Irrigation nécessaire", "reason": "Faibles précipitations"}

    def _assess_overall_risk(self, weather_data):
        """Évalue le risque global"""
        alerts = weather_data.agricultural_alerts
        high_risks = [a for a in alerts if a['severity'] == 'HIGH']

        if len(high_risks) >= 2:
            return "RISQUE ÉLEVÉ - Surveillance renforcée nécessaire"
        elif len(high_risks) >= 1:
            return "RISQUE MODÉRÉ - Précautions recommandées"
        else:
            return "RISQUE FAIBLE - Conditions favorables"

    # AJOUT DE LA MÉTHODE MANQUANTE
    def analyze_risks(self, weather_data: Dict) -> List[Dict]:
        """Analyse les risques agricoles - Méthode utilisée par le serializer"""
        risks = []
        forecast_days = weather_data.get('forecast', {}).get('forecastday', [])

        for day in forecast_days:
            risks.extend(self._analyze_day_risks(day))

        return risks

    def _analyze_day_risks(self, day_data: Dict) -> List[Dict]:
        """Analyse les risques pour une journée spécifique"""
        risks = []
        day_info = day_data['day']
        date = day_data['date']

        # Heavy Rain Risk
        if day_info['totalprecip_mm'] > self.risk_thresholds['heavy_rain']:
            risks.append({
                'type': 'HEAVY_RAIN',
                'date': date,
                'severity': 'HIGH',
                'message': f"🌧️ Pluie intense prévue: {day_info['totalprecip_mm']}mm",
                'metrics': {
                    'precipitation': day_info['totalprecip_mm'],
                    'chance_of_rain': day_info.get('daily_chance_of_rain', 0)
                }
            })

        # Frost Risk
        if day_info['mintemp_c'] < self.risk_thresholds['frost']:
            risks.append({
                'type': 'FROST_RISK',
                'date': date,
                'severity': 'HIGH',
                'message': f"❄️ Risque de gel: {day_info['mintemp_c']}°C",
                'metrics': {
                    'min_temperature': day_info['mintemp_c'],
                    'avg_temperature': day_info['avgtemp_c']
                }
            })

        # Drought Risk
        if (day_info['totalprecip_mm'] <= self.risk_thresholds['drought']['precip'] and
                day_info['avgtemp_c'] > self.risk_thresholds['drought']['temp']):
            risks.append({
                'type': 'DROUGHT_RISK',
                'date': date,
                'severity': 'MEDIUM',
                'message': f"🌵 Risque de sécheresse: {day_info['avgtemp_c']}°C sans pluie",
                'metrics': {
                    'precipitation': day_info['totalprecip_mm'],
                    'temperature': day_info['avgtemp_c']
                }
            })

        # Strong Wind Risk
        if day_info['maxwind_kph'] > self.risk_thresholds['strong_wind']:
            risks.append({
                'type': 'STRONG_WIND',
                'date': date,
                'severity': 'MEDIUM',
                'message': f"💨 Vent fort: {day_info['maxwind_kph']} km/h",
                'metrics': {
                    'wind_speed': day_info['maxwind_kph'],
                    'wind_direction': day_info.get('wind_dir', 'N/A')
                }
            })

        # High Humidity Risk (maladies fongiques)
        if day_info['avghumidity'] > self.risk_thresholds['high_humidity']:
            risks.append({
                'type': 'HIGH_HUMIDITY',
                'date': date,
                'severity': 'MEDIUM',
                'message': f"💧 Humidité élevée: {day_info['avghumidity']}%",
                'metrics': {
                    'humidity': day_info['avghumidity'],
                    'condition': day_info['condition']['text']
                }
            })

        return risks

# SmartSaha/services/weather_api_client.py
import requests
import logging
from typing import Dict, Optional
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


class WeatherAPIClient:
    """Client pour l'API WeatherAPI.com"""

    def __init__(self):
        self.api_key = getattr(settings, 'WEATHER_API_KEY', 'bb9e11ef9ae046bf953133218252008')
        self.base_url = "http://api.weatherapi.com/v1"

    def get_forecast(self, latitude: float, longitude: float, days: int = 8) -> Optional[Dict]:
        """Récupère les prévisions météo pour une localisation"""
        try:
            url = f"{self.base_url}/forecast.json"
            params = {
                'key': self.api_key,
                'q': f"{latitude},{longitude}",
                'days': days,
                'lang': 'fr'
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur API météo: {e}")
            return None
        except ValueError as e:
            logger.error(f"Erreur parsing JSON: {e}")
            return None


import json
from typing import Dict, Optional, Tuple


class WeatherDataCollector:
    """Collecteur adapté à votre structure Parcel"""

    def __init__(self):
        self.api_client = WeatherAPIClient()
        from SmartSaha.services import WeatherDataService
        self.weather_service = WeatherDataService()

    def _extract_center_from_points(self, points_data) -> Tuple[Optional[float], Optional[float]]:
        """Extrait le centre du polygone de points"""
        try:
            if isinstance(points_data, str):
                points = json.loads(points_data)
            else:
                points = points_data

            if not points or len(points) == 0:
                return None, None

            # Calcul du centre du polygone
            total_lat = 0
            total_lng = 0
            count = 0

            for point in points:
                total_lat += point['lat']
                total_lng += point['lng']
                count += 1

            return total_lat / count, total_lng / count

        except (json.JSONDecodeError, KeyError, TypeError) as e:
            print(f"Erreur extraction centre: {e}")
            return None, None

    def collect_and_save_weather_data(self, parcel) -> Dict:
        """Collecte et sauvegarde les données météo pour une parcelle"""
        try:
            # Extraire le centre du polygone
            latitude, longitude = self._extract_center_from_points(parcel.points)

            if not latitude or not longitude:
                return {
                    'success': False,
                    'error': 'Impossible de déterminer le centre de la parcelle'
                }

            # Récupération des données météo
            weather_data = self.api_client.get_forecast(latitude, longitude, days=8)

            if not weather_data:
                return {
                    'success': False,
                    'error': 'Impossible de récupérer les données météo'
                }

            # Sauvegarde dans la base
            result = self.weather_service.process_weather_data(weather_data, parcel)

            print(f"Données météo sauvegardées pour {parcel.parcel_name}: {result['alerts_count']} alertes")

            return {
                'success': True,
                'weather_data_id': result['weather_data'].id,
                'alerts_generated': result['alerts_count'],
                'risk_level': result['risk_level'],
                'location': weather_data['location']['name'],
                'coordinates_used': {'lat': latitude, 'lng': longitude}
            }

        except Exception as e:
            print(f"Erreur collecte météo pour {parcel.parcel_name}: {e}")
            return {
                'success': False,
                'error': str(e)
            }