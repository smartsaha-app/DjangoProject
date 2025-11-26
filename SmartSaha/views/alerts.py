# views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Count, Q

from SmartSaha.models import Parcel, Alert
from SmartSaha.services import ParcelDataService, AlertService
from SmartSaha.serializers import AlertSerializer


class AlertViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des alertes
    """
    permission_classes = [IsAuthenticated]
    serializer_class = AlertSerializer

    def get_queryset(self):
        """Retourne uniquement les alertes de l'utilisateur connecté"""
        return Alert.objects.filter(parcel__owner=self.request.user).select_related('parcel').order_by('-created_at')

    def list(self, request, *args, **kwargs):
        """Liste des alertes avec filtres"""
        queryset = self.filter_queryset(self.get_queryset())

        # Filtres supplémentaires
        parcel_uuid = request.query_params.get('parcel_uuid')
        severity = request.query_params.get('severity')
        is_read = request.query_params.get('is_read')
        alert_type = request.query_params.get('type')

        if parcel_uuid:
            queryset = queryset.filter(parcel__uuid=parcel_uuid)
        if severity:
            queryset = queryset.filter(severity=severity)
        if is_read:
            queryset = queryset.filter(is_read=is_read.lower() == 'true')
        if alert_type:
            queryset = queryset.filter(type__icontains=alert_type)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def generate_parcel_alerts(self, request):
        """
        Génère et retourne les alertes en temps réel pour une parcelle
        URL: /api/alerts/generate_parcel_alerts/?parcel_uuid=xxx
        """
        parcel_uuid = request.query_params.get('parcel_uuid')

        if not parcel_uuid:
            return Response(
                {"error": "Le paramètre parcel_uuid est requis"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            parcel = Parcel.objects.get(uuid=parcel_uuid, owner=request.user)

            # Récupérer données avec gestion d'erreur
            try:
                weather_data = ParcelDataService.get_weather_analysis(parcel)
            except Exception as e:
                weather_data = {}
                print(f"Erreur récupération météo: {e}")

            try:
                soil_data = ParcelDataService.fetch_soil(parcel)
            except Exception as e:
                soil_data = {}
                print(f"Erreur récupération sol: {e}")

            # Générer alertes avec gestion d'erreur
            try:
                weather_alerts = AlertService.generate_weather_alerts(parcel, weather_data)
                soil_alerts = AlertService.generate_soil_alerts(parcel, soil_data)
                task_alerts = AlertService.generate_task_alerts(parcel)

                all_alerts = weather_alerts + soil_alerts + task_alerts
            except Exception as e:
                return Response(
                    {"error": f"Erreur génération alertes: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            # Sauvegarder en base (uniquement les nouvelles)
            saved_count = 0
            for alert_data in all_alerts:
                _, created = Alert.objects.get_or_create(
                    parcel=parcel,
                    type=alert_data['type'],
                    severity=alert_data['severity'],
                    alert_date=alert_data['date'],
                    defaults={
                        'message': alert_data['message'],
                        'action': alert_data.get('action', ''),
                        'is_read': False
                    }
                )
                if created:
                    saved_count += 1

            # Compter les priorités
            high_priority = len([a for a in all_alerts if a['severity'] in ['HIGH', 'CRITICAL']])
            medium_priority = len([a for a in all_alerts if a['severity'] == 'MEDIUM'])
            low_priority = len([a for a in all_alerts if a['severity'] == 'LOW'])

            return Response({
                'alerts': all_alerts,
                'total_generated': len(all_alerts),
                'saved_count': saved_count,
                'high_priority': high_priority,
                'medium_priority': medium_priority,
                'low_priority': low_priority,
                'parcel_name': parcel.parcel_name,
                'parcel_uuid': str(parcel.uuid),
                'generated_at': timezone.now().isoformat()
            })

        except Parcel.DoesNotExist:
            return Response(
                {"error": "Parcelle non trouvée"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": f"Erreur serveur: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def dashboard_stats(self, request):
        """
        Statistiques des alertes pour le dashboard
        URL: /api/alerts/dashboard_stats/
        """
        queryset = self.get_queryset()

        stats = {
            'total_alerts': queryset.count(),
            'unread_count': queryset.filter(is_read=False).count(),
            'high_priority_count': queryset.filter(severity__in=['HIGH', 'CRITICAL'], is_read=False).count(),
            'medium_priority_count': queryset.filter(severity='MEDIUM', is_read=False).count(),
            'low_priority_count': queryset.filter(severity='LOW', is_read=False).count(),
            'recent_alerts': AlertSerializer(
                queryset.filter(is_read=False).order_by('-created_at')[:5],
                many=True
            ).data
        }

        # Stats par type d'alerte
        type_stats = queryset.filter(is_read=False).values('type').annotate(
            count=Count('id'),
            high_priority=Count('id', filter=Q(severity__in=['HIGH', 'CRITICAL']))
        ).order_by('-count')

        stats['alert_types'] = list(type_stats)

        # Stats par parcelle
        parcels = Parcel.objects.filter(owner=request.user)
        parcel_stats = []

        for parcel in parcels:
            parcel_alerts = queryset.filter(parcel=parcel, is_read=False)
            parcel_stats.append({
                'parcel_name': parcel.parcel_name,
                'parcel_uuid': str(parcel.uuid),
                'alert_count': parcel_alerts.count(),
                'high_priority': parcel_alerts.filter(severity__in=['HIGH', 'CRITICAL']).count(),
                'medium_priority': parcel_alerts.filter(severity='MEDIUM').count()
            })

        stats['parcel_breakdown'] = parcel_stats

        return Response(stats)

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """
        Marquer une alerte comme lue
        URL: /api/alerts/{id}/mark_read/
        """
        try:
            alert = self.get_object()
            alert.is_read = True
            alert.save()

            return Response({
                "message": "Alerte marquée comme lue",
                "alert_id": alert.id,
                "alert_type": alert.type,
                "is_read": True
            })
        except Exception as e:
            return Response(
                {"error": f"Erreur: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """
        Marquer toutes les alertes comme lues
        URL: /api/alerts/mark_all_read/
        """
        try:
            parcel_uuid = request.data.get('parcel_uuid')
            severity = request.data.get('severity')
            alert_type = request.data.get('type')

            queryset = self.get_queryset().filter(is_read=False)

            if parcel_uuid:
                queryset = queryset.filter(parcel__uuid=parcel_uuid)
            if severity:
                queryset = queryset.filter(severity=severity)
            if alert_type:
                queryset = queryset.filter(type__icontains=alert_type)

            updated_count = queryset.update(is_read=True)

            return Response({
                "message": f"{updated_count} alertes marquées comme lues",
                "updated_count": updated_count,
                "filters_applied": {
                    "parcel_uuid": parcel_uuid,
                    "severity": severity,
                    "type": alert_type
                }
            })
        except Exception as e:
            return Response(
                {"error": f"Erreur: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """
        Nombre d'alertes non lues
        URL: /api/alerts/unread_count/
        """
        try:
            parcel_uuid = request.query_params.get('parcel_uuid')
            severity = request.query_params.get('severity')

            queryset = self.get_queryset().filter(is_read=False)

            if parcel_uuid:
                queryset = queryset.filter(parcel__uuid=parcel_uuid)
            if severity:
                queryset = queryset.filter(severity=severity)

            count = queryset.count()

            return Response({
                "unread_count": count,
                "filters": {
                    "parcel_uuid": parcel_uuid,
                    "severity": severity
                }
            })
        except Exception as e:
            return Response(
                {"error": f"Erreur: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'])
    def generate_comprehensive_alerts(self, request):
        """
        Génère toutes les alertes complètes pour une parcelle
        URL: /api/alerts/generate_comprehensive_alerts/?parcel_uuid=xxx
        """
        parcel_uuid = request.query_params.get('parcel_uuid')

        if not parcel_uuid:
            return Response(
                {"error": "Le paramètre parcel_uuid est requis"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            parcel = Parcel.objects.get(uuid=parcel_uuid, owner=request.user)

            # Vérifier si les méthodes existent dans AlertService
            if not hasattr(AlertService, 'generate_all_alerts'):
                return Response(
                    {"error": "Fonction generate_all_alerts non disponible"},
                    status=status.HTTP_501_NOT_IMPLEMENTED
                )

            # Générer TOUTES les alertes
            all_alerts = AlertService.generate_all_alerts(parcel)

            # Vérifier si get_alert_statistics existe
            if hasattr(AlertService, 'get_alert_statistics'):
                stats = AlertService.get_alert_statistics(all_alerts)
            else:
                # Fallback si la méthode n'existe pas
                stats = {
                    'total': len(all_alerts),
                    'critical': len([a for a in all_alerts if a.get('severity') == 'CRITICAL']),
                    'high': len([a for a in all_alerts if a.get('severity') == 'HIGH']),
                    'medium': len([a for a in all_alerts if a.get('severity') == 'MEDIUM']),
                    'low': len([a for a in all_alerts if a.get('severity') == 'LOW'])
                }

            # Sauvegarder les alertes générées
            saved_count = 0
            for alert_data in all_alerts:
                _, created = Alert.objects.get_or_create(
                    parcel=parcel,
                    type=alert_data['type'],
                    severity=alert_data['severity'],
                    alert_date=alert_data['date'],
                    defaults={
                        'message': alert_data['message'],
                        'action': alert_data.get('action', ''),
                        'is_read': False
                    }
                )
                if created:
                    saved_count += 1

            return Response({
                'alerts': all_alerts,
                'statistics': stats,
                'saved_count': saved_count,
                'parcel_name': parcel.parcel_name,
                'parcel_uuid': str(parcel.uuid),
                'generated_at': timezone.now().isoformat()
            })

        except Parcel.DoesNotExist:
            return Response(
                {"error": "Parcelle non trouvée"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": f"Erreur lors de la génération: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def types_summary(self, request):
        """
        Résumé des alertes par type
        URL: /api/alerts/types_summary/
        """
        try:
            queryset = self.get_queryset().filter(is_read=False)

            types_summary = queryset.values('type', 'severity').annotate(
                count=Count('id')
            ).order_by('-count')

            return Response({
                'types_summary': list(types_summary),
                'total_types': len(types_summary)
            })
        except Exception as e:
            return Response(
                {"error": f"Erreur: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['delete'])
    def delete_old_alerts(self, request):
        """
        Supprimer les alertes anciennes (plus de 30 jours)
        URL: /api/alerts/delete_old_alerts/
        """
        try:
            from django.utils import timezone
            from datetime import timedelta

            cutoff_date = timezone.now() - timedelta(days=30)
            old_alerts = self.get_queryset().filter(created_at__lt=cutoff_date)

            deleted_count = old_alerts.count()
            old_alerts.delete()

            return Response({
                "message": f"{deleted_count} alertes anciennes supprimées",
                "cutoff_date": cutoff_date.isoformat(),
                "deleted_count": deleted_count
            })
        except Exception as e:
            return Response(
                {"error": f"Erreur: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )