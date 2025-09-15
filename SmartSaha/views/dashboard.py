from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action

from SmartSaha.services import DashboardService

class DashboardViewSet(viewsets.ViewSet):
    """
    ViewSet pour exposer le Dashboard BI complet pour un utilisateur donné.
    Récupère les données de parcelles, sols, climat, rendements et tâches.
    """

    @action(detail=False, methods=["get"])
    def full_dashboard(self, request):
        """
        GET /api/dashboard/full_dashboard/
        Retourne le dashboard complet pour l'utilisateur connecté.
        """
        user = request.user
        dashboard_service = DashboardService(user)
        data = dashboard_service.get_full_dashboard()
        return Response(data)
