# SmartSaha/views/weather_views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from SmartSaha.models import WeatherData, AgriculturalAlert
from SmartSaha.serializers import WeatherDataSerializer, AgriculturalAlertSerializer
from SmartSaha.services import WeatherDataService, AgriculturalAnalyzer


class WeatherDataViewSet(viewsets.ModelViewSet):
    """Vues concrètes pour WeatherData"""
    serializer_class = WeatherDataSerializer
    queryset = WeatherData.objects.all()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.weather_service = WeatherDataService()
        self.analyzer = AgriculturalAnalyzer()

    @action(detail=False, methods=['post'])
    def process_weather_data(self, request):
        """Endpoint pour traiter les données météo brutes"""
        try:
            raw_data = request.data.get('weather_data')
            parcel_id = request.data.get('parcel_id')

            # Récupération de la parcelle (à adapter selon votre modèle Parcel)
            from SmartSaha.models import Parcel
            parcel = get_object_or_404(Parcel, id=parcel_id)

            # Traitement des données
            result = self.weather_service.process_weather_data(raw_data, parcel)

            return Response({
                'success': True,
                'weather_data_id': result['weather_data'].id,
                'alerts_generated': result['alerts_count'],
                'risk_level': result['risk_level'],
                'message': f"{result['alerts_count']} alertes générées"
            })

        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def agricultural_analysis(self, request, pk=None):
        """Analyse agricole complète des données météo"""
        weather_data = self.get_object()

        analysis = self.analyzer.analyze_weather_data(weather_data)

        return Response({
            'success': True,
            'analysis': analysis
        })

    @action(detail=False, methods=['get'])
    def parcel_weather(self, request):
        """Récupère les dernières données météo d'une parcelle"""
        parcel_id = request.query_params.get('parcel_id')

        if not parcel_id:
            return Response(
                {'error': 'Le paramètre parcel_id est requis'},
                status=status.HTTP_400_BAD_REQUEST
            )

        latest_weather = WeatherData.objects.filter(
            parcel_id=parcel_id
        ).order_by('-created_at').first()

        if not latest_weather:
            return Response({
                'success': False,
                'message': 'Aucune donnée météo trouvée pour cette parcelle'
            })

        serializer = self.get_serializer(latest_weather)
        return Response({
            'success': True,
            'weather_data': serializer.data
        })


class AgriculturalAlertViewSet(viewsets.ReadOnlyModelViewSet):
    """Vues pour les alertes agricoles"""
    serializer_class = AgriculturalAlertSerializer

    def get_queryset(self):
        queryset = AgriculturalAlert.objects.filter(is_active=True)

        # Filtres
        parcel_id = self.request.query_params.get('parcel_id')
        severity = self.request.query_params.get('severity')

        if parcel_id:
            queryset = queryset.filter(weather_data__parcel_id=parcel_id)
        if severity:
            queryset = queryset.filter(severity=severity)

        return queryset.order_by('-alert_date')

    @action(detail=False, methods=['get'])
    def active_alerts(self, request):
        """Alertes actives pour le dashboard"""
        parcel_id = request.query_params.get('parcel_id')

        alerts = self.get_queryset()
        if parcel_id:
            alerts = alerts.filter(weather_data__parcel_id=parcel_id)

        high_priority = alerts.filter(severity='HIGH')
        medium_priority = alerts.filter(severity='MEDIUM')

        return Response({
            'total_alerts': alerts.count(),
            'high_priority_count': high_priority.count(),
            'medium_priority_count': medium_priority.count(),
            'recent_alerts': AgriculturalAlertSerializer(alerts[:10], many=True).data
        })


# SmartSaha/views/weather_collection_views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from SmartSaha.models import Parcel
from SmartSaha.services import WeatherDataCollector


class WeatherCollectionViewSet(viewsets.ViewSet):
    """Vues pour la collecte automatique des données météo"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.weather_collector = WeatherDataCollector()

    @action(detail=False, methods=['post'])
    def collect_parcel_weather(self, request):
        """Collecte les données météo pour une parcelle spécifique"""
        parcel_uuid = request.data.get('parcel_uuid')  # Changé de parcel_id à parcel_uuid

        if not parcel_uuid:
            return Response(
                {'error': 'Le paramètre parcel_uuid est requis'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # CORRECTION : Utiliser uuid au lieu de id
            parcel = get_object_or_404(Parcel, uuid=parcel_uuid)

            # Vérifier que la parcelle a des points
            if not parcel.points:
                return Response({
                    'success': False,
                    'error': 'La parcelle doit avoir des points GPS définis'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Collecte des données (sans passer lat/long en paramètres)
            result = self.weather_collector.collect_and_save_weather_data(parcel)

            if result['success']:
                return Response({
                    'success': True,
                    'message': f'Données météo collectées pour {parcel.parcel_name}',
                    'data': result
                })
            else:
                return Response({
                    'success': False,
                    'error': result['error']
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Parcel.DoesNotExist:
            return Response({
                'success': False,
                'error': f'Parcelle avec UUID {parcel_uuid} non trouvée'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'success': False,
                'error': f'Erreur lors de la collecte: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'])
    def collect_all_parcels_weather(self, request):
        """Collecte les données météo pour toutes les parcelles avec points"""
        try:
            parcels = Parcel.objects.filter(points__isnull=False).exclude(points=[])

            results = []
            total_success = 0

            for parcel in parcels:
                result = self.weather_collector.collect_and_save_weather_data(parcel)

                results.append({
                    'parcel_uuid': str(parcel.uuid),
                    'parcel_name': parcel.parcel_name,
                    'success': result['success'],
                    'alerts_generated': result.get('alerts_generated', 0),
                    'coordinates_used': result.get('coordinates_used'),
                    'error': result.get('error')
                })

                if result['success']:
                    total_success += 1

            return Response({
                'success': True,
                'message': f'Collecte terminée: {total_success}/{len(parcels)} réussites',
                'results': results
            })

        except Exception as e:
            return Response({
                'success': False,
                'error': f'Erreur lors de la collecte globale: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)