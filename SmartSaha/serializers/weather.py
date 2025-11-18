# agriculture/serializers/weather_serializers.py
from rest_framework import serializers
from SmartSaha.models import WeatherData, AgriculturalAlert


class WeatherDataSerializer(serializers.ModelSerializer):
    parcel_name = serializers.CharField(source='parcel.name', read_only=True)
    risk_analysis = serializers.SerializerMethodField()
    agricultural_summary = serializers.SerializerMethodField()

    class Meta:
        model = WeatherData
        fields = [
            'id', 'parcel_name', 'start', 'end', 'data_type', 'risk_level',
            'current_temperature', 'total_precipitation', 'risk_analysis',
            'agricultural_summary', 'created_at'
        ]

    def get_risk_analysis(self, obj):
        from SmartSaha.services import AgriculturalAnalyzer
        analyzer = AgriculturalAnalyzer()
        return analyzer.analyze_risks(obj.data)

    def get_agricultural_summary(self, obj):
        return {
            'alerts_count': len(obj.agricultural_alerts),
            'optimal_planting_days': obj.optimal_planting_days,
            'irrigation_recommendation': obj.irrigation_recommendation
        }


class AgriculturalAlertSerializer(serializers.ModelSerializer):
    weather_data_id = serializers.IntegerField(source='weather_data.id', read_only=True)
    parcel_name = serializers.CharField(source='weather_data.parcel.name', read_only=True)

    class Meta:
        model = AgriculturalAlert
        fields = [
            'id', 'alert_type', 'message', 'recommendation', 'severity',
            'alert_date', 'is_active', 'weather_data_id', 'parcel_name'
        ]