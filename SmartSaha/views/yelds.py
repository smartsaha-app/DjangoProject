from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from SmartSaha.models import YieldRecord
from SmartSaha.serializers import YieldRecordSerializer
from SmartSaha.services import YieldAnalyticsService


class YieldRecordViewSet(viewsets.ModelViewSet):
    queryset = YieldRecord.objects.all()
    serializer_class = YieldRecordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Filtrer les rendements de l'utilisateur connecté uniquement
        """
        return YieldRecord.objects.filter(parcelCrop__parcel__owner=self.request.user)


class YieldAnalyticsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        service = YieldAnalyticsService(user=request.user)
        stats_json = service.get_user_stats()

        if not stats_json:
            return Response({"detail": "Aucune donnée de rendement disponible."}, status=404)

        return Response(stats_json)