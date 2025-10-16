from rest_framework import serializers

from suivi_evaluation.models import DataLog, CustomField, CustomFieldValue

# TODO: gestion de permission par rapport au role de l' utilisateur
class DataLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataLog
        fields = '__all__'

# TODO: gestion de permission par rapport au role de l' utilisateur
class CustomFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomField
        fields = '__all__'

# TODO: gestion de permission par rapport au role de l' utilisateur
class CustomFieldValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomFieldValue
        fields = '__all__'
