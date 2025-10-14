from rest_framework import viewsets
from ..models import DataLog, CustomField, CustomFieldValue
from ..serializers.datalog import (
    DataLogSerializer,
    CustomFieldSerializer,
    CustomFieldValueSerializer
)

class DataLogViewSet(viewsets.ModelViewSet):
    """
    Gère les journaux de données (création, modification, suppression)
    """
    queryset = DataLog.objects.all()
    serializer_class = DataLogSerializer


class CustomFieldViewSet(viewsets.ModelViewSet):
    """
    Gère la définition des champs personnalisés dynamiques
    """
    queryset = CustomField.objects.all()
    serializer_class = CustomFieldSerializer


class CustomFieldValueViewSet(viewsets.ModelViewSet):
    """
    Gère les valeurs associées aux champs personnalisés
    """
    queryset = CustomFieldValue.objects.all()
    serializer_class = CustomFieldValueSerializer
