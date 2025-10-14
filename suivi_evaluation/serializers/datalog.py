from rest_framework import serializers

from suivi_evaluation.models import DataLog, CustomField, CustomFieldValue

class DataLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataLog
        fields = '__all__'


class CustomFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomField
        fields = '__all__'


class CustomFieldValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomFieldValue
        fields = '__all__'
