from rest_framework import serializers
from SmartSaha.models import Parcel, ParcelPoint


class ParcelPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParcelPoint
        fields = ['latitude', 'longitude', 'order']


class ParcelSerializer(serializers.ModelSerializer):
    # On autorise l’écriture des points directement
    parcel_points = ParcelPointSerializer(many=True)

    class Meta:
        model = Parcel
        fields = ['uuid', 'owner', 'parcel_name', 'points', 'parcel_points', 'created_at', 'updated_at']
        read_only_fields = ['uuid', 'created_at', 'updated_at']

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
