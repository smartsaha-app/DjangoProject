from rest_framework import serializers
from SmartSaha.models import Parcel, ParcelPoint


class ParcelPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParcelPoint
        fields = ['latitude', 'longitude', 'order']


class ParcelSerializer(serializers.ModelSerializer):
    parcel_points = ParcelPointSerializer(many=True)

    # AJOUTS : Nouvelles propriétés pour l'API météo
    has_gps_points = serializers.SerializerMethodField()
    points_count = serializers.SerializerMethodField()
    center_coordinates = serializers.SerializerMethodField()

    class Meta:
        model = Parcel
        fields = [
            'uuid', 'owner', 'parcel_name', 'points', 'parcel_points',
            'created_at', 'updated_at',
            # AJOUTS :
            'has_gps_points', 'points_count', 'center_coordinates'
        ]
        read_only_fields = ['uuid', 'created_at', 'updated_at']

    # AJOUTS : Méthodes pour l'API météo
    def get_has_gps_points(self, obj):
        """Vérifie si la parcelle a des points GPS"""
        return bool(obj.points) and len(obj.points) > 0

    def get_points_count(self, obj):
        """Retourne le nombre de points GPS"""
        if obj.points and isinstance(obj.points, list):
            return len(obj.points)
        return 0

    def get_center_coordinates(self, obj):
        """Calcule le centre du polygone pour l'API météo"""
        if not obj.points or not isinstance(obj.points, list) or len(obj.points) == 0:
            return None

        try:
            total_lat = 0
            total_lng = 0
            count = 0

            for point in obj.points:
                total_lat += point['lat']
                total_lng += point['lng']
                count += 1

            return {
                'lat': round(total_lat / count, 6),
                'lng': round(total_lng / count, 6)
            }
        except (KeyError, TypeError):
            return None

    # VOS MÉTHODES EXISTANTES (conservées)
    def create(self, validated_data):
        points_data = validated_data.pop('parcel_points', [])
        parcel = Parcel.objects.create(**validated_data)

        for point_data in points_data:
            ParcelPoint.objects.create(parcel=parcel, **point_data)

        # Optionnel : mettre à jour le champ points JSON
        parcel.points = [{'lat': p['latitude'], 'lng': p['longitude']} for p in points_data]
        parcel.save()

        return parcel

    def update(self, instance, validated_data):
        points_data = validated_data.pop('parcel_points', None)

        # Mise à jour simple des champs de Parcel
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Mise à jour des points si fournis
        if points_data is not None:
            # Supprimer les anciens points
            instance.parcel_points.all().delete()
            for point_data in points_data:
                ParcelPoint.objects.create(parcel=instance, **point_data)

            instance.points = [{'lat': p['latitude'], 'lng': p['longitude']} for p in points_data]
            instance.save()

        return instance


class ParcelWeatherSerializer(serializers.ModelSerializer):
    """Serializer léger spécialement pour l'API météo"""
    center_coordinates = serializers.SerializerMethodField()
    points_count = serializers.SerializerMethodField()

    class Meta:
        model = Parcel
        fields = ['uuid', 'parcel_name', 'points_count', 'center_coordinates']

    def get_center_coordinates(self, obj):
        """Calcule le centre du polygone pour l'API météo"""
        if not obj.points or not isinstance(obj.points, list) or len(obj.points) == 0:
            return None

        try:
            total_lat = 0
            total_lng = 0
            count = 0

            for point in obj.points:
                total_lat += point['lat']
                total_lng += point['lng']
                count += 1

            return {
                'lat': round(total_lat / count, 6),
                'lng': round(total_lng / count, 6)
            }
        except (KeyError, TypeError):
            return None

    def get_points_count(self, obj):
        if obj.points and isinstance(obj.points, list):
            return len(obj.points)
        return 0