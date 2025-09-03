from django.db import models

# -------------------------------
# Rendements
# -------------------------------
class YieldRecord(models.Model):
    id = models.BigAutoField(primary_key=True)
    parcel = models.ForeignKey('SmartSaha.Parcel', on_delete=models.CASCADE)
    crop = models.ForeignKey('SmartSaha.Crop', on_delete=models.CASCADE)
    date = models.DateField()
    yield_amount = models.FloatField()
    area = models.FloatField()
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey('SmartSaha.User', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.crop.parcel_name

