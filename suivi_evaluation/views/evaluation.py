# suivi_evaluation/views/certifications.py
from rest_framework import viewsets
from ..models import CertificationType, Certification, CertificationAudit
from ..serializers.evaluation import (
    CertificationTypeSerializer, CertificationSerializer, CertificationAuditSerializer
)

class CertificationTypeViewSet(viewsets.ModelViewSet):
    queryset = CertificationType.objects.all()
    serializer_class = CertificationTypeSerializer


class CertificationViewSet(viewsets.ModelViewSet):
    queryset = Certification.objects.all()
    serializer_class = CertificationSerializer


class CertificationAuditViewSet(viewsets.ModelViewSet):
    queryset = CertificationAudit.objects.all()
    serializer_class = CertificationAuditSerializer


# class ParcelEvaluationViewSet(viewsets.ModelViewSet):
#     """
#     Gère les évaluations des parcelles (risques, productivité, etc.)
#     """
#     queryset = ParcelEvaluation.objects.all()
#     serializer_class = ParcelEvaluationSerializer
#
#
# class GeoLayerViewSet(viewsets.ModelViewSet):
#     """
#     Gère les couches géographiques (région, district, commune, etc.)
#     """
#     queryset = GeoLayer.objects.all()
#     serializer_class = GeoLayerSerializer

