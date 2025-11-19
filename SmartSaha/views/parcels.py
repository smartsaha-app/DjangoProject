from django.core.cache import cache
from django.db.models import Sum, Avg
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from SmartSaha.models import Parcel, ParcelPoint, ParcelCrop, YieldRecord
from SmartSaha.permissions import logger
from SmartSaha.serializers import ParcelSerializer, ParcelPointSerializer, ParcelWeatherSerializer
from SmartSaha.services import ParcelService, ParcelDataService
from SmartSaha.mixins.cache_mixins import CacheInvalidationMixin

CACHE_TIMEOUT = 60 * 15  # 15 minutes


class ParcelViewSet(viewsets.ModelViewSet):
    """Vues pour les parcelles - Accès restreint au propriétaire"""
    serializer_class = ParcelSerializer
    lookup_field = 'uuid'
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Retourne UNIQUEMENT les parcelles de l'utilisateur connecté"""
        if getattr(self, 'swagger_fake_view', False):
            return Parcel.objects.none()

        queryset = Parcel.objects.filter(owner=self.request.user)

        # Optimisation pour les relations fréquentes
        queryset = queryset.select_related('owner')

        return queryset

    def perform_create(self, serializer):
        """Assigne automatiquement l'utilisateur connecté comme propriétaire"""
        serializer.save(owner=self.request.user)

    def perform_update(self, serializer):
        """Vérifie que l'utilisateur reste propriétaire"""
        instance = serializer.instance
        if instance.owner != self.request.user:
            raise PermissionDenied("Vous ne pouvez pas modifier cette parcelle")
        serializer.save()

    # Action pour l'API météo
    @action(detail=False, methods=['get'])
    def with_gps(self, request):
        """Liste les parcelles avec points GPS - UNIQUEMENT celles de l'utilisateur"""
        parcels = self.get_queryset().filter(
            points__isnull=False
        ).exclude(points=[])

        serializer = ParcelWeatherSerializer(parcels, many=True)

        return Response({
            'success': True,
            'count': parcels.count(),
            'parcels': serializer.data
        })

    # Détail d'une parcelle pour météo
    @action(detail=True, methods=['get'])
    def weather_info(self, request, uuid=None):
        """Informations météo - Vérification propriétaire automatique via get_object()"""
        parcel = self.get_object()  # Déjà filtré par get_queryset()

        serializer = ParcelWeatherSerializer(parcel)

        return Response({
            'success': True,
            'parcel': serializer.data,
            'can_collect_weather': bool(parcel.points) and len(parcel.points) > 0
        })
class ParcelPointViewSet(CacheInvalidationMixin, viewsets.ModelViewSet):
    queryset = ParcelPoint.objects.all()
    serializer_class = ParcelPointSerializer
    cache_prefix = "parcel_point"
    use_object_cache = True

    # Exemple dans ParcelPointViewSet
    def perform_create(self, serializer):
        instance = serializer.save()
        self.invalidate_cache(getattr(instance, "parcel", instance))
        return instance


class ParcelFullDataViewSet(CacheInvalidationMixin, viewsets.ViewSet):
    cache_prefix = "parcel_full_data"
    use_object_cache = True

    @action(detail=True, methods=["get"])
    def full_data(self, request, pk=None):
        # key = self.get_cache_key(pk)
        # cached = cache.get(key)
        # if cached:
        #     return Response(cached)

        try:
            parcel = Parcel.objects.get(uuid=pk, owner=request.user)
            complete_data = ParcelDataService.get_complete_parcel_data(str(parcel.uuid))

            if not complete_data:
                return Response({"error": "Parcel data not found"}, status=404)

            response = {
                "parcel": complete_data['parcel'],
                "soil_data": ParcelDataService.serialize_soil_data(complete_data['soil_data']),
                "weather_data": ParcelDataService.serialize_weather_data(complete_data['weather_data']),
                "parcel_crops": complete_data['crops'],
                "yield_records": complete_data['yield_records'],
                "tasks": complete_data['tasks'],
                "tasks_summary": complete_data['tasks_summary']
            }

            # cache.set(key, response, timeout=CACHE_TIMEOUT)
            return Response(response)

        except Parcel.DoesNotExist:
            return Response({"error": "Parcel not found"}, status=404)
        except Exception as e:
            logger.error(f"Error in ParcelFullDataViewSet.full_data: {str(e)}")
            return Response({"error": "Internal server error"}, status=500)

    # Optionnel : Ajouter une action pour les tâches uniquement
    @action(detail=True, methods=["get"])
    def tasks(self, request, pk=None):
        """Endpoint dédié pour récupérer uniquement les tâches d'une parcelle"""
        try:
            parcel = Parcel.objects.get(uuid=pk, owner=request.user)
            tasks_data = ParcelDataService.build_parcel_tasks(parcel)
            return Response(tasks_data)
        except Parcel.DoesNotExist:
            return Response({"error": "Parcel not found"}, status=404)

    # Optionnel : Ajouter une action pour le résumé des tâches
    @action(detail=True, methods=["get"])
    def tasks_summary(self, request, pk=None):
        """Endpoint dédié pour le résumé des tâches (dashboard)"""
        try:
            parcel = Parcel.objects.get(uuid=pk, owner=request.user)
            tasks_summary = ParcelDataService.get_tasks_summary(parcel)
            return Response(tasks_summary)
        except Parcel.DoesNotExist:
            return Response({"error": "Parcel not found"}, status=404)

    @action(detail=True, methods=["post"])
    def refresh_soil_data(self, request, pk=None):
        """Endpoint pour forcer le rafraîchissement des données sol"""
        try:
            parcel = Parcel.objects.get(uuid=pk, owner=request.user)
            soil_data = ParcelDataService.refresh_soil_data(parcel)
            return Response({
                "status": "success",
                "message": "Données sol rafraîchies",
                "soil_data": ParcelDataService.serialize_soil_data(soil_data)
            })
        except Parcel.DoesNotExist:
            return Response({"error": "Parcel not found"}, status=404)
