from django.db import models
from django.contrib.auth import get_user_model
import uuid
User = get_user_model()


class Report(models.Model):
    class ReportType(models.TextChoices):
        PROGRESS = 'PROGRESS', 'Rapport d’avancement'
        FINANCIAL = 'FINANCIAL', 'Rapport financier'
        IMPACT = 'IMPACT', 'Rapport d’impact'
        AUDIT = 'AUDIT', 'Rapport d’audit'

    class ReportStatus(models.TextChoices):
        DRAFT = 'DRAFT', 'Brouillon'
        SUBMITTED = 'SUBMITTED', 'Soumis'
        APPROVED = 'APPROVED', 'Approuvé'

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150)
    type = models.CharField(
        max_length=20,
        choices=ReportType.choices,
        default=ReportType.PROGRESS
    )
    period_start = models.DateField()
    period_end = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=ReportStatus.choices,
        default=ReportStatus.DRAFT
    )
    organisation_id = models.IntegerField()
    created_by = models.ForeignKey(User, related_name="reports_created", on_delete=models.SET_NULL, null=True)
    updated_by = models.ForeignKey(User, related_name="reports_updated", on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class ReportData(models.Model):
    class DataKey(models.TextChoices):
        TOTAL_HA = 'TOTAL_HA', 'Superficie totale (ha)'
        YIELD_AVG = 'YIELD_AVG', 'Rendement moyen'
        PROD_COUNT = 'PROD_COUNT', 'Nombre de producteurs'
        COST_TOTAL = 'COST_TOTAL', 'Coût total'
        INCOME_TOTAL = 'INCOME_TOTAL', 'Revenu total'

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name="data")
    key = models.CharField(max_length=100)
    value = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class ReportAttachment(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name="attachments")
    file_path = models.FileField(upload_to="reports/")
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class ReportLog(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name="logs")
    action = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    old_data = models.JSONField(blank=True, null=True)
    new_data = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class CertificationType(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class CertificationAudit(models.Model):

    class AuditResult(models.TextChoices):
        PASS = 'PASS', 'Réussi'
        FAIL = 'FAIL', 'Échec'
        PENDING = 'PENDING', 'En attente'

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name="audits")
    cert_type = models.ForeignKey(CertificationType, on_delete=models.CASCADE, related_name="certifications")
    auditor = models.CharField(max_length=100)
    result = models.CharField(max_length=20, choices=AuditResult.choices)
    date_audit = models.DateField()
    remarks = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Certification(models.Model):
    class CertStatus(models.TextChoices):
        VALID = 'VALID', 'Valide'
        EXPIRED = 'EXPIRED', 'Expirée'
        REVOKED = 'REVOKED', 'Révoquée'
        PENDING = 'PENDING', 'En attente'

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cert_type = models.ForeignKey(CertificationType, on_delete=models.CASCADE, related_name="certifications_type")
    issued_by = models.CharField(max_length=100)
    issued_at = models.DateField()
    expires_at = models.DateField()
    status = models.CharField(max_length=20, choices=CertStatus.choices, default=CertStatus.PENDING)
    file = models.FileField(upload_to="certifications/")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)