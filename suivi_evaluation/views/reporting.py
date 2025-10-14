# suivi_evaluation/views/reports.py
from rest_framework import viewsets
from ..models import Report, ReportData, ReportAttachment
from ..serializers.reporting import (
    ReportSerializer, ReportDataSerializer, ReportAttachmentSerializer
)

class ReportViewSet(viewsets.ModelViewSet):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer


class ReportDataViewSet(viewsets.ModelViewSet):
    queryset = ReportData.objects.all()
    serializer_class = ReportDataSerializer


class ReportAttachmentViewSet(viewsets.ModelViewSet):
    queryset = ReportAttachment.objects.all()
    serializer_class = ReportAttachmentSerializer
