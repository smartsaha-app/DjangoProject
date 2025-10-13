from django.db import models
from django.contrib.auth import get_user_model
import uuid
User = get_user_model()


class ParcelEvaluation(models.Model):
    class RiskLevel(models.TextChoices):
        LOW = 'LOW', 'Faible'
        MEDIUM = 'MEDIUM', 'Moyen'
        HIGH = 'HIGH', 'Élevé'

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    parcel_id = models.UUIDField()
    period = models.CharField(max_length=50)
    compliance_score = models.FloatField(default=0)
    yield_score = models.FloatField(default=0)
    risk_level = models.CharField(max_length=20, choices=RiskLevel.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



class GeoLayer(models.Model):
    LAYER_TYPES = [
        ("heatmap", "Heatmap"),
        ("polygon", "Polygon"),
        ("marker", "Marker"),
    ]
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=LAYER_TYPES)
    geojson = models.JSONField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
