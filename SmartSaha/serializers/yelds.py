from rest_framework import serializers
from SmartSaha.models import YieldRecord

class YieldRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = YieldRecord
        fields = '__all__'
