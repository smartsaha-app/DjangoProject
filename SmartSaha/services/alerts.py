# services/alert_service.py
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Q
from SmartSaha.models import WeatherData

class AlertService:
    @staticmethod
    def generate_weather_alerts(parcel, weather_data):
        """Génère des alertes météo basées sur les cultures"""
        alerts = []

        # Récupérer les cultures de la parcelle (adaptation à votre modèle)
        current_crops = []
        try:
            if hasattr(parcel, 'parcel_crops') and hasattr(parcel.parcel_crops, 'all'):
                current_crops = [pc.crop.name.lower() for pc in parcel.parcel_crops.all()]
            elif hasattr(parcel, 'crops') and hasattr(parcel.crops, 'all'):
                current_crops = [crop.name.lower() for crop in parcel.crops.all()]
        except Exception as e:
            print(f"Erreur récupération cultures: {e}")
            current_crops = []

        # Conversion de l'objet WeatherData en dict si nécessaire
        if hasattr(weather_data, '__dict__'):
            weather_dict = weather_data.__dict__
        elif hasattr(weather_data, 'get'):
            weather_dict = weather_data
        else:
            weather_dict = {}

        # Accès sécurisé aux données météo
        daily_forecast = []
        try:
            # Essayer différents formats de données
            if hasattr(weather_data, 'daily_forecast'):
                daily_forecast = weather_data.daily_forecast
            elif 'daily_forecast' in weather_dict:
                daily_forecast = weather_dict['daily_forecast']
            elif hasattr(weather_data, 'forecast'):
                daily_forecast = weather_data.forecast
        except Exception as e:
            print(f"Erreur accès forecast: {e}")

        # Alertes température - avec gestion d'erreur
        for day in daily_forecast[:3]:  # 3 prochains jours
            try:
                # Accès sécurisé aux données du jour
                if hasattr(day, '__dict__'):
                    day_dict = day.__dict__
                else:
                    day_dict = day

                # Récupération des températures avec valeurs par défaut
                min_temp = getattr(day, 'min_temp', None) or day_dict.get('min_temp', 0)
                max_temp = getattr(day, 'max_temp', None) or day_dict.get('max_temp', 0)
                date_str = getattr(day, 'date', None) or day_dict.get('date', datetime.now().date().isoformat())

                # Alerte gel
                if min_temp < 5:  # Seuil gel critique
                    alerts.append({
                        'type': '❄️ GEL EXTRÊME',
                        'message': f"Gel sévère prévu ({min_temp}°C) le {date_str}",
                        'severity': 'CRITICAL',
                        'action': 'Protection urgente nécessaire - voiles, chauffage',
                        'date': date_str
                    })
                elif min_temp < 10 and any(
                        crop in current_crops for crop in ['maïs', 'tomate', 'riz', 'vigne', 'arbres fruitiers']):
                    alerts.append({
                        'type': '❄️ RISQUE GEL',
                        'message': f"Risque de gel ({min_temp}°C) le {date_str}",
                        'severity': 'HIGH',
                        'action': 'Protéger les cultures sensibles avec voile',
                        'date': date_str
                    })

                # Alerte canicule
                if max_temp > 40:
                    alerts.append({
                        'type': '🔥 CANICULE',
                        'message': f"Température extrême ({max_temp}°C) le {date_str}",
                        'severity': 'CRITICAL',
                        'action': 'Irrigation renforcée, ombrage si possible',
                        'date': date_str
                    })
                elif max_temp > 35:
                    alerts.append({
                        'type': '🌡️ CHALEUR EXTRÊME',
                        'message': f"Température élevée ({max_temp}°C) le {date_str}",
                        'severity': 'HIGH',
                        'action': 'Augmenter irrigation pour éviter stress thermique',
                        'date': date_str
                    })

            except Exception as e:
                print(f"Erreur traitement jour météo: {e}")
                continue

        # Alertes pluie - avec gestion d'erreur
        try:
            total_rain_7d = 0
            for day in daily_forecast[:7]:
                if hasattr(day, '__dict__'):
                    day_dict = day.__dict__
                else:
                    day_dict = day

                precip = getattr(day, 'total_precip', None) or day_dict.get('total_precip', 0) or day_dict.get(
                    'precipitation', 0)
                total_rain_7d += precip

            if total_rain_7d > 100:
                alerts.append({
                    'type': '🌧️ INONDATION',
                    'message': f"Pluies très importantes ({total_rain_7d}mm sur 7 jours) - risque inondation",
                    'severity': 'CRITICAL',
                    'action': 'Vérifier drainage urgent, préparer pompage',
                    'date': datetime.now().date().isoformat()
                })
            elif total_rain_7d > 50:
                alerts.append({
                    'type': '🌧️ EXCÈS PLUIE',
                    'message': f"Fortes pluies prévues ({total_rain_7d}mm sur 7 jours)",
                    'severity': 'MEDIUM',
                    'action': 'Vérifier le drainage des parcelles',
                    'date': datetime.now().date().isoformat()
                })
            elif total_rain_7d < 5:
                alerts.append({
                    'type': '💧 SÉCHERESSE SÉVÈRE',
                    'message': f"Très faibles précipitations ({total_rain_7d}mm sur 7 jours)",
                    'severity': 'HIGH',
                    'action': 'Irrigation intensive nécessaire - risque perte de récolte',
                    'date': datetime.now().date().isoformat()
                })
            elif total_rain_7d < 10:
                alerts.append({
                    'type': '💧 SÉCHERESSE',
                    'message': f"Faibles précipitations ({total_rain_7d}mm sur 7 jours)",
                    'severity': 'MEDIUM',
                    'action': 'Renforcer irrigation - risque stress hydrique',
                    'date': datetime.now().date().isoformat()
                })

        except Exception as e:
            print(f"Erreur calcul pluie: {e}")

        return alerts

    @staticmethod
    def generate_soil_alerts(parcel, soil_data):
        """Alertes basées sur l'analyse du sol"""
        alerts = []

        try:
            # Conversion en dict si nécessaire
            if hasattr(soil_data, '__dict__'):
                soil_dict = soil_data.__dict__
            else:
                soil_dict = soil_data

            # pH analysis - avec accès sécurisé
            ph = None
            if hasattr(soil_data, 'phh2o'):
                if hasattr(soil_data.phh2o, 'mean'):
                    ph = soil_data.phh2o.mean
                elif hasattr(soil_data.phh2o, 'get'):
                    ph = soil_data.phh2o.get('mean')
            elif 'phh2o' in soil_dict:
                ph_data = soil_dict['phh2o']
                if hasattr(ph_data, 'mean'):
                    ph = ph_data.mean
                elif isinstance(ph_data, dict):
                    ph = ph_data.get('mean')

            if ph and ph < 5.5:
                alerts.append({
                    'type': '🧪 pH ACIDE',
                    'message': f"pH du sol acide ({ph}) pour la plupart des cultures",
                    'severity': 'MEDIUM',
                    'action': 'Appliquer 1-2 tonnes/ha de chaux agricole',
                    'date': datetime.now().date().isoformat()
                })

            # Nitrogen analysis
            nitrogen = None
            if hasattr(soil_data, 'nitrogen'):
                if hasattr(soil_data.nitrogen, 'mean'):
                    nitrogen = soil_data.nitrogen.mean
            elif 'nitrogen' in soil_dict:
                nitro_data = soil_dict['nitrogen']
                if hasattr(nitro_data, 'mean'):
                    nitrogen = nitro_data.mean
                elif isinstance(nitro_data, dict):
                    nitrogen = nitro_data.get('mean')

            if nitrogen and nitrogen < 1.0:
                alerts.append({
                    'type': '🌱 CARENCE AZOTE',
                    'message': f"Taux d'azote faible ({nitrogen} g/kg)",
                    'severity': 'HIGH',
                    'action': 'Appliquer engrais azoté (urée ou fumier)',
                    'date': datetime.now().date().isoformat()
                })

        except Exception as e:
            print(f"Erreur analyse sol: {e}")

        return alerts

    @staticmethod
    def generate_task_alerts(parcel):
        """Alertes pour tâches en retard ou urgentes"""
        alerts = []
        today = timezone.now().date()

        try:
            # Vérifier si le modèle Task existe
            from SmartSaha.models import Task

            # Tâches en retard
            overdue_tasks = Task.objects.filter(
                parcel=parcel,
                completed_at__isnull=True,
                due_date__lt=today
            )

            for task in overdue_tasks:
                days_late = (today - task.due_date).days
                alerts.append({
                    'type': '⏰ TÂCHE EN RETARD',
                    'message': f"{task.name} - {days_late} jour(s) de retard",
                    'severity': 'HIGH' if days_late > 7 else 'MEDIUM',
                    'action': 'Exécuter cette tâche dès que possible',
                    'date': task.due_date.isoformat()
                })

            # Tâches urgentes (dans 3 jours)
            urgent_tasks = Task.objects.filter(
                parcel=parcelCrop.parcel,
                completed_at__isnull=True,
                due_date__range=[today, today + timedelta(days=3)]
            )

            for task in urgent_tasks:
                alerts.append({
                    'type': '🔔 TÂCHE URGENTE',
                    'message': f"{task.name} - Échéance le {task.due_date}",
                    'severity': 'MEDIUM',
                    'action': 'Planifier cette tâche rapidement',
                    'date': task.due_date.isoformat()
                })

        except Exception as e:
            print(f"Erreur tâches: {e}")

        return alerts

    @staticmethod
    def generate_irrigation_alerts(parcel, soil_moisture_data):
        """Alertes basées sur l'humidité du sol"""
        alerts = []

        current_moisture = soil_moisture_data.get('current_moisture')
        if current_moisture:
            if current_moisture < 0.2:  # 20% d'humidité
                alerts.append({
                    'type': '💧 SOL TRÈS SEC',
                    'message': f"Humidité du sol très basse ({current_moisture * 100:.1f}%)",
                    'severity': 'HIGH',
                    'action': 'Irrigation immédiate nécessaire - risque stress hydrique sévère',
                    'date': datetime.now().date().isoformat()
                })
            elif current_moisture < 0.3:
                alerts.append({
                    'type': '💧 SOL SEC',
                    'message': f"Humidité du sol basse ({current_moisture * 100:.1f}%)",
                    'severity': 'MEDIUM',
                    'action': 'Programmer irrigation dans les 24h',
                    'date': datetime.now().date().isoformat()
                })
            elif current_moisture > 0.8:
                alerts.append({
                    'type': '🌊 EXCÈS D\'EAU',
                    'message': f"Sol saturé en eau ({current_moisture * 100:.1f}%) - risque asphyxie racinaire",
                    'severity': 'HIGH',
                    'action': 'Arrêter irrigation, améliorer drainage',
                    'date': datetime.now().date().isoformat()
                })

        return alerts


    @staticmethod
    def generate_pest_disease_alerts(parcel, weather_data):
        """Alertes maladies et ravageurs basées sur les conditions météo"""
        alerts = []

        # Conditions favorables mildiou (humidité + température)
        for day in weather_data.get('daily_forecast', [])[:5]:
            humidity = day.get('humidity', 0)
            temp = day.get('avg_temp', 0)

            if humidity > 80 and 15 <= temp <= 25:
                alerts.append({
                    'type': '🦠 RISQUE MILDIU',
                    'message': f"Conditions favorables au mildiou le {day['date']}",
                    'severity': 'MEDIUM',
                    'action': 'Surveiller cultures, traitement préventif si nécessaire',
                    'date': day['date']
                })

            # Conditions favorables oïdium
            if humidity > 70 and temp > 25:
                alerts.append({
                    'type': '🍂 RISQUE OÏDIUM',
                    'message': f"Conditions favorables à l'oïdium le {day['date']}",
                    'severity': 'MEDIUM',
                    'action': 'Traiter préventivement avec soufre',
                    'date': day['date']
                })

        return alerts


    @staticmethod
    def generate_growth_stage_alerts(parcel):
        """Alertes basées sur le stade de croissance des cultures"""
        alerts = []
        today = timezone.now().date()

        # Cette partie dépend de votre modèle de suivi de croissance
        # Exemple simplifié :
        if hasattr(parcel, 'growth_stage'):
            growth_stage = parcel.growth_stage
            if growth_stage == 'flowering':
                alerts.append({
                    'type': '🌸 FLORAISON EN COURS',
                    'message': "Stade floraison - période critique pour irrigation et nutrition",
                    'severity': 'MEDIUM',
                    'action': 'Éviter stress hydrique, surveiller pollinisation',
                    'date': today.isoformat()
                })
            elif growth_stage == 'fruit_development':
                alerts.append({
                    'type': '🍎 DÉVELOPPEMENT FRUITS',
                    'message': "Stade développement fruits - besoins nutritionnels élevés",
                    'severity': 'MEDIUM',
                    'action': 'Fertilisation potassium, irrigation régulière',
                    'date': today.isoformat()
                })

        return alerts


    @staticmethod
    def generate_all_alerts(parcel, weather_data=None, soil_data=None, soil_moisture_data=None):
        """
        Génère toutes les alertes pour une parcelle
        """
        all_alerts = []

        # Récupérer les données si non fournies
        if weather_data is None:
            from SmartSaha.services import ParcelDataService
            weather_data = ParcelDataService.get_weather_analysis(parcel) if hasattr(ParcelDataService,
                                                                                     'get_weather_analysis') else {}

        if soil_data is None:
            from SmartSaha.services import ParcelDataService
            soil_data = ParcelDataService.fetch_soil(parcel) if hasattr(ParcelDataService, 'fetch_soil') else {}

        # Générer toutes les catégories d'alertes
        all_alerts.extend(AlertService.generate_weather_alerts(parcel, weather_data))
        all_alerts.extend(AlertService.generate_soil_alerts(parcel, soil_data))
        all_alerts.extend(AlertService.generate_task_alerts(parcel))
        all_alerts.extend(AlertService.generate_irrigation_alerts(parcel, soil_moisture_data or {}))
        all_alerts.extend(AlertService.generate_pest_disease_alerts(parcel, weather_data))
        all_alerts.extend(AlertService.generate_growth_stage_alerts(parcel))

        # Trier par sévérité (CRITICAL > HIGH > MEDIUM > LOW)
        severity_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
        all_alerts.sort(key=lambda x: severity_order.get(x['severity'], 4))

        return all_alerts


    @staticmethod
    def get_alert_statistics(alerts):
        """Retourne des statistiques sur les alertes"""
        stats = {
            'total': len(alerts),
            'critical': len([a for a in alerts if a['severity'] == 'CRITICAL']),
            'high': len([a for a in alerts if a['severity'] == 'HIGH']),
            'medium': len([a for a in alerts if a['severity'] == 'MEDIUM']),
            'low': len([a for a in alerts if a['severity'] == 'LOW']),
            'by_type': {}
        }

        for alert in alerts:
            alert_type = alert['type']
            if alert_type not in stats['by_type']:
                stats['by_type'][alert_type] = 0
            stats['by_type'][alert_type] += 1

        return stats