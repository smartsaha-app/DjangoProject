from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from SmartSaha.models import Parcel, ParcelPoint
from SmartSaha.serializers import ParcelSerializer, ParcelPointSerializer
from SmartSaha.services import ParcelService, ParcelDataService


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


class ParcelFullDataViewSet(viewsets.ViewSet):

    @action(detail=True, methods=["get"])
    def full_data(self, request, pk=None):
        try:
            parcel = Parcel.objects.get(pk=pk)
        except Parcel.DoesNotExist:
            return Response({"error": "Parcel not found"}, status=404)

        try:
            soil_obj = ParcelDataService.fetch_soil(parcel)
            climate_obj = ParcelDataService.fetch_climate(parcel,
                                                          start=request.GET.get("start"),
                                                          end=request.GET.get("end"))
        except ValueError as e:
            return Response({"error": str(e)}, status=400)

        response = {
            "parcel": {
                "id": str(parcel.uuid),
                "name": parcel.parcel_name,
                # "area": parcel.area,
                "points": parcel.points
            },
            "soil_data": soil_obj.data if soil_obj else None,
            "climate_data": climate_obj.data if climate_obj else None,
            "parcel_crops": ParcelDataService.build_parcel_crops(parcel),
            "yield_records": ParcelDataService.build_yield_records(parcel)
        }

        return Response(response)


def parcel_full_data_page(request, parcel_uuid):
    return render(request, "parcel_full_data.html", {"parcel_uuid": parcel_uuid})