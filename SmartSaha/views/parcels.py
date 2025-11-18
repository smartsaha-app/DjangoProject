from django.core.cache import cache
from django.db.models import Sum, Avg
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from SmartSaha.models import Parcel, ParcelPoint, ParcelCrop, YieldRecord
from SmartSaha.serializers import ParcelSerializer, ParcelPointSerializer, ParcelWeatherSerializer
from SmartSaha.services import ParcelService, ParcelDataService
from SmartSaha.mixins.cache_mixins import CacheInvalidationMixin

CACHE_TIMEOUT = 60 * 15  # 15 minutes


class ParcelViewSet(viewsets.ModelViewSet):
    """Vues pour les parcelles - utilise votre serializer existant"""
    queryset = Parcel.objects.all()
    serializer_class = ParcelSerializer  # Votre serializer existant
    lookup_field = 'uuid'

    # AJOUT : Action pour l'API météo
    @action(detail=False, methods=['get'])
    def with_gps(self, request):
        """Liste les parcelles avec points GPS (pour API météo)"""
        parcels = Parcel.objects.filter(points__isnull=False).exclude(points=[])

        # Utilise le serializer spécialisé météo pour une réponse légère
        serializer = ParcelWeatherSerializer(parcels, many=True)

        return Response({
            'success': True,
            'count': parcels.count(),
            'parcels': serializer.data
        })

    # AJOUT : Détail d'une parcelle pour météo
    @action(detail=True, methods=['get'])
    def weather_info(self, request, uuid=None):
        """Informations spécifiques pour l'API météo"""
        parcel = self.get_object()

        # Utilise le serializer spécialisé météo
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
        key = self.get_cache_key(pk)
        cached = cache.get(key)
        if cached:
            return Response(cached)

        try:
            parcel = Parcel.objects.select_related("owner").prefetch_related(
                "parcel_crops__yieldrecord_set",
                "parcel_points"
            ).get(pk=pk, owner=request.user)
        except Parcel.DoesNotExist:
            return Response({"error": "Parcel not found"}, status=404)

        # Soil + Climate
        soil_obj = ParcelDataService.fetch_soil(parcel)
        climate_obj = ParcelDataService.fetch_climate(parcel,
                                                      start=request.GET.get("start"),
                                                      end=request.GET.get("end"))

        # Parcel crops + yield
        parcel_crops = parcel.parcel_crops.all().annotate(
            total_yield=Sum("yieldrecord__yield_amount"),
            avg_yield=Avg("yieldrecord__yield_amount")
        )
        crops_data = [
            {"id": pc.id, "crop_name": pc.crop.name if pc.crop else None,
             "total_yield": pc.total_yield, "avg_yield": pc.avg_yield}
            for pc in parcel_crops
        ]

        yield_records = YieldRecord.objects.filter(parcelCrop__parcel=parcel).values(
            "id", "yield_amount", "date", "parcelCrop_id"
        )

        response = {
            "parcel": {"id": str(parcel.uuid), "name": parcel.parcel_name, "points": parcel.points},
            "soil_data": soil_obj.data if soil_obj else None,
            "climate_data": climate_obj.data if climate_obj else None,
            "parcel_crops": crops_data,
            "yield_records": list(yield_records)
        }

        cache.set(key, response, timeout=CACHE_TIMEOUT)
        return Response(response)
