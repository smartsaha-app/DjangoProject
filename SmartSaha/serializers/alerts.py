# serializers.py
from rest_framework import serializers
from SmartSaha.models import Alert, Parcel


class ParcelShortSerializer(serializers.ModelSerializer):
    """Serializer léger pour les parcelles dans les alertes"""

    class Meta:
        model = Parcel
        fields = ['uuid', 'parcel_name']  # Retiré 'area'

    def to_representation(self, instance):
        """Représentation avec calcul de surface si nécessaire"""
        data = super().to_representation(instance)

        # Optionnel: calculer la surface à la volée
        from SmartSaha.services import ParcelDataService
        area = ParcelDataService.calculate_area(instance)
        if area:
            data['area_hectares'] = area

        return data


class AlertSerializer(serializers.ModelSerializer):
    """Serializer principal pour les alertes"""

    # Champs calculés
    days_since_created = serializers.SerializerMethodField()
    parcel_info = serializers.SerializerMethodField()
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)

    class Meta:
        model = Alert
        fields = [
            'id',
            'type',
            'message',
            'severity',
            'severity_display',
            'action',
            'is_read',
            'created_at',
            'alert_date',
            'days_since_created',
            'parcel',
            'parcel_info'
        ]
        read_only_fields = ['id', 'created_at']

    def get_days_since_created(self, obj):
        """Nombre de jours depuis la création de l'alerte"""
        from django.utils import timezone
        if obj.created_at:
            delta = timezone.now().date() - obj.created_at.date()
            return delta.days
        return 0

    def get_parcel_info(self, obj):
        """Informations légères sur la parcelle"""
        return ParcelShortSerializer(obj.parcel).data