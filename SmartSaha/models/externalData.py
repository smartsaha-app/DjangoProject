from django.db import models

class SoilData(models.Model):
    parcel = models.ForeignKey("SmartSaha.Parcel", on_delete=models.CASCADE)
    data = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

class ClimateData(models.Model):
    parcel = models.ForeignKey("SmartSaha.Parcel", on_delete=models.CASCADE)
    data = models.JSONField()
    start = models.DateField()
    end = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
