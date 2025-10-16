from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from SmartSaha.mixins.cache_mixins import CacheInvalidationMixin
from SmartSaha.models import YieldRecord
from SmartSaha.serializers import YieldRecordSerializer
from SmartSaha.services import YieldAnalyticsService


class YieldRecordViewSet(CacheInvalidationMixin, viewsets.ModelViewSet):
    queryset = YieldRecord.objects.all()
    serializer_class = YieldRecordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return YieldRecord.objects.none()
        return YieldRecord.objects.filter(parcelCrop__parcel__owner=self.request.user)


class YieldAnalyticsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        service = YieldAnalyticsService(user=request.user)
        stats_json = service.get_user_stats()

        if not stats_json:
            return Response({"detail": "Aucune donnée de rendement disponible."}, status=404)

        return Response(stats_json)