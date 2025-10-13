from rest_framework import serializers
from suivi_evaluation.models import Indicator, IndicatorValue

from django.contrib.auth import get_user_model

User = get_user_model()

class IndicatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Indicator
        fields = '__all__'


class IndicatorValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = IndicatorValue
        fields = '__all__'

#
# class AlertSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Alert
#         fields = '__all__'
#
#
# class DashboardConfigSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = DashboardConfig
#         fields = '__all__'
