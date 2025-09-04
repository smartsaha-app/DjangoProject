from rest_framework import viewsets, permissions

from SmartSaha.models import Crop, StatusCrop, Variety, ParcelCrop
from SmartSaha.serializers import CropSerializer, StatusCropSerializer, VarietySerializer, ParcelCropSerializer


class CropViewSet(viewsets.ModelViewSet):
    queryset = Crop.objects.all()
    serializer_class = CropSerializer
    permission_classes = [permissions.AllowAny]

class StatusCropViewSet(viewsets.ModelViewSet):
    queryset = StatusCrop.objects.all()
    serializer_class = StatusCropSerializer
    permission_classes = [permissions.AllowAny]

class VarietyViewSet(viewsets.ModelViewSet):
    queryset = Variety.objects.all()
    serializer_class = VarietySerializer
    permission_classes = [permissions.AllowAny]

class ParcelCropViewSet(viewsets.ModelViewSet):
    queryset = ParcelCrop.objects.all()
    serializer_class = ParcelCropSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Filtrer les tâches de l'utilisateur connecté
        return ParcelCrop.objects.filter(parcel__owner=self.request.user)

