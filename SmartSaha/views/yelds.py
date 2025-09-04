from rest_framework import viewsets, permissions
from SmartSaha.models import YieldRecord
from SmartSaha.serializers import YieldRecordSerializer

class YieldRecordViewSet(viewsets.ModelViewSet):
    queryset = YieldRecord.objects.all()
    serializer_class = YieldRecordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Filtrer les rendements de l'utilisateur connecté uniquement
        """
        return YieldRecord.objects.filter(parcelCrop__parcel__owner=self.request.user)

