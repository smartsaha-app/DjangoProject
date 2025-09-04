from django.http import JsonResponse
from django.views import View
from rest_framework import viewsets, permissions
from SmartSaha.models import Parcel, ParcelPoint
from SmartSaha.serializers import ParcelSerializer, ParcelPointSerializer
from SmartSaha.services import ParcelService


class ParcelViewSet(viewsets.ModelViewSet):
    queryset = Parcel.objects.all()
    serializer_class = ParcelSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Filtrer les tâches de l'utilisateur connecté
        return Parcel.objects.filter(owner= self.request.user)

class ParcelPointViewSet(viewsets.ModelViewSet):
    queryset = ParcelPoint.objects.all()
    serializer_class = ParcelPointSerializer

class ParcelCreateView(View):

    def post(self, request):
        """
        :param request:
        :return:
        """
        # données du frontend
        points = request.POST.get('points')
        from SmartSaha.models import Parcel
        parcel = Parcel.objects.create(owner=request.user, parcel_name="Ma Parcelle")
        ParcelService(parcel).add_points_bulk(points)
        return JsonResponse({"success": True})
