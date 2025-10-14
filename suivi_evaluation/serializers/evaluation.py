from rest_framework import serializers
from suivi_evaluation.models import CertificationType, CertificationAudit, Certification
from suivi_evaluation.serializers import ReportSerializer


class CertificationTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CertificationType
        fields = '__all__'


class CertificationSerializer(serializers.ModelSerializer):
    cert_type = CertificationTypeSerializer(read_only=True)

    class Meta:
        model = Certification
        fields = '__all__'


class CertificationAuditSerializer(serializers.ModelSerializer):
    cert_type = CertificationTypeSerializer(read_only=True)
    report = ReportSerializer(read_only=True)

    class Meta:
        model = CertificationAudit
        fields = '__all__'
