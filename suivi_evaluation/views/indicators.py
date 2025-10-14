# suivi_evaluation/views/indicators.py
from rest_framework import viewsets
from ..models import Indicator, IndicatorValue
from ..serializers.indicators import IndicatorSerializer, IndicatorValueSerializer

class IndicatorViewSet(viewsets.ModelViewSet):
    queryset = Indicator.objects.all()
    serializer_class = IndicatorSerializer


class IndicatorValueViewSet(viewsets.ModelViewSet):
    queryset = IndicatorValue.objects.all()
    serializer_class = IndicatorValueSerializer
