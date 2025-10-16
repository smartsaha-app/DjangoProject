from rest_framework import viewsets, permissions

from SmartSaha.mixins.cache_mixins import CacheInvalidationMixin
from SmartSaha.models import Crop, StatusCrop, Variety, ParcelCrop
from SmartSaha.serializers import CropSerializer, StatusCropSerializer, VarietySerializer, ParcelCropSerializer


class CropViewSet(CacheInvalidationMixin, viewsets.ModelViewSet):
    queryset = Crop.objects.all()
    serializer_class = CropSerializer
    permission_classes = [permissions.AllowAny]

class StatusCropViewSet(CacheInvalidationMixin, viewsets.ModelViewSet):
    queryset = StatusCrop.objects.all()
    serializer_class = StatusCropSerializer
    permission_classes = [permissions.AllowAny]

class VarietyViewSet(CacheInvalidationMixin, viewsets.ModelViewSet):
    queryset = Variety.objects.all()
    serializer_class = VarietySerializer
    permission_classes = [permissions.AllowAny]

class ParcelCropViewSet(CacheInvalidationMixin, viewsets.ModelViewSet):
    queryset = ParcelCrop.objects.all()
    serializer_class = ParcelCropSerializer
    permission_classes = [permissions.IsAuthenticated]

def get_queryset(self):
    if getattr(self, 'swagger_fake_view', False):
        return ParcelCrop.objects.none()
    return ParcelCrop.objects.filter(parcel__owner=self.request.user)

