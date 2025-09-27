from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Sum, Avg
from django.db.models.functions import ExtractYear
from django.utils import timezone

from SmartSaha.models import Parcel, ParcelCrop, YieldRecord, YieldForecast, Crop, ClimateData

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

@login_required(login_url='login')
def dashboard(request):
    # Récupérer toutes les parcelles
    all_parcels = Parcel.objects.all()

    service = DashboardService(user=request.user)
    dashboard_data = service.get_full_dashboard()

    # Calcul du rendement total (toutes parcelles confondues)
    rendement_total = sum([y['summary']['total_yield'] for y in dashboard_data['yield_summary'] if y['summary']])
    print(rendement_total)
    # Construire une vue simplifiée des parcelles attendue par le template
    parcelles = []
    for parcel in all_parcels:
        # Dernière culture (si disponible)
        last_parcel_crop = (
            ParcelCrop.objects.filter(parcel=parcel)
            .order_by('-created_at')
            .first()
        )
        culture_name = last_parcel_crop.crop.name if last_parcel_crop and last_parcel_crop.crop else 'N/A'
        superficie = last_parcel_crop.area if last_parcel_crop else 0

        # Rendement cumulé pour cette parcelle
        rendement_par_parcelle = (
            YieldRecord.objects.filter(parcelCrop__parcel=parcel)
            .aggregate(total=Sum('yield_amount'))['total'] or 0
        )

        parcelles.append({
            'id': parcel.uuid,
            'nom': parcel.parcel_name,
            'culture': culture_name,
            'superficie': superficie,
            'rendement': rendement_par_parcelle,
        })

    # Prévision simple: moyenne des prévisions existantes (fallback 0)
    prevision = int(YieldForecast.objects.aggregate(avg=Avg('predicted_yield'))['avg'] or 0)

    # Utilisateur connecté
    user = request.user if request.user.is_authenticated else None
    user_display = user.username if user else "Invité"
    avatar_url = (
        f"https://ui-avatars.com/api/?name={user_display}&background=10b981&color=ffffff&size=64"
    )

    # Cultures pour le modal
    crops = list(Crop.objects.values_list('name', flat=True))

    # Filtres pour statistiques
    parcel_names = list(all_parcels.values_list('parcel_name', flat=True))
    years = list(
        YieldRecord.objects.annotate(y=ExtractYear('date')).order_by('y').values_list('y', flat=True).distinct()
    )

    # Données pour le graphique de stats: totaux par mois sur les 6 derniers mois
    today = timezone.now().date()
    # Construire les 6 derniers mois (labels FR abrégés)
    month_labels = []
    month_values = []
    for i in range(5, -1, -1):
        # reculer i mois
        year = (today.year if today.month - i > 0 else today.year - 1)
        month = ((today.month - i - 1) % 12) + 1
        label = ["Jan", "Fév", "Mar", "Avr", "Mai", "Juin", "Juil", "Août", "Sep", "Oct", "Nov", "Déc"][month-1]
        month_labels.append(label)
        month_sum = YieldRecord.objects.filter(date__year=year, date__month=month).aggregate(s=Sum('yield_amount'))['s'] or 0
        month_values.append(month_sum)

    # Données météo à partir de ClimateData si disponible (on prend la plus récente)
    temp_max = []
    temp_min = []
    precip = []
    days_labels = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]
    latest_climate = ClimateData.objects.order_by('-created_at').first()
    if latest_climate and isinstance(latest_climate.data, dict):
        # Essayer d'interpréter quelques formes communes {"temperature_max": [...], "temperature_min": [...], "precipitations": [...]}
        data = latest_climate.data
        temp_max = list(data.get('temperature_max', [])[:7])
        temp_min = list(data.get('temperature_min', [])[:7])
        precip = list(data.get('precipitations', [])[:7])
    # si aucune donnée, laisser des tableaux vides -> Chart.js affichera un graphique vide plutôt que des données statiques

    context = {
        'parcelles': parcelles,
        'rendement_total': rendement_total,
        'prevision': prevision,
        'user_display': user_display,
        'avatar_url': avatar_url,
        'crops': crops,
        'parcel_names': parcel_names,
        'years': years,
        'stats_labels': month_labels,
        'stats_values': month_values,
        'temp_labels': days_labels,
        'temp_max': temp_max,
        'temp_min': temp_min,
        'rain_labels': days_labels,
        'rain_values': precip,
        "dashboard": dashboard_data
    }

    return render(request, 'dashboard.html', context)
