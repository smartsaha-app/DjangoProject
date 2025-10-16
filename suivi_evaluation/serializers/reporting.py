from rest_framework import serializers

from suivi_evaluation.models import Report, ReportData, ReportAttachment
# TODO: gestion de permission par rapport au role de l' utilisateur

class ReportDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportData
        fields = '__all__'

# TODO: gestion de permission par rapport au role de l' utilisateur

class ReportAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportAttachment
        fields = '__all__'

# TODO: gestion de permission par rapport au role de l' utilisateur

class ReportSerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField()
    updated_by = serializers.StringRelatedField()

    class Meta:
        model = Report
        fields = '__all__'
