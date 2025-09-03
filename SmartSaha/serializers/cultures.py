from rest_framework import serializers

from SmartSaha.models import Variety, StatusCrop, Crop, ParcelCrop, Parcel


class VarietySerializer(serializers.ModelSerializer):
    class Meta:
        model = Variety
        fields = "__all__"

class StatusCropSerializer(serializers.ModelSerializer):
    class Meta:
        model = StatusCrop
        fields = "__all__"

class CropSerializer(serializers.ModelSerializer):
    variety = VarietySerializer(read_only=True)
    variety_id = serializers.PrimaryKeyRelatedField(
        queryset=Variety.objects.all(), source="variety", write_only=True, required=False
    )

    class Meta:
        model = Crop
        fields = ["id", "name", "variety", "variety_id", "created_at"]

class ParcelCropSerializer(serializers.ModelSerializer):
    parcel = serializers.PrimaryKeyRelatedField(queryset=Parcel.objects.all())
    crop = CropSerializer(read_only=True)
    crop_id = serializers.PrimaryKeyRelatedField(
        queryset=Crop.objects.all(), source="crop", write_only=True
    )
    status = StatusCropSerializer(read_only=True)
    status_id = serializers.PrimaryKeyRelatedField(
        queryset=StatusCrop.objects.all(), source="status", write_only=True, required=False
    )

    class Meta:
        model = ParcelCrop
        fields = [
            "id", "parcel", "crop", "crop_id",
            "planting_date", "harvest_date", "area",
            "status", "status_id", "created_at"
        ]
