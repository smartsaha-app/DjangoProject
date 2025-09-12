from django.db import models

# -------------------------------
# Rendements
# -------------------------------
class YieldRecord(models.Model):
    id = models.BigAutoField(primary_key=True)
    parcelCrop = models.ForeignKey('SmartSaha.ParcelCrop', on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateField()
    yield_amount = models.FloatField()
    area = models.FloatField()
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.parcelCrop.parcel.parcel_name} - {self.date} - {self.yield_amount} - {self.area} - {self.created_at}"


class YieldForecast(models.Model):
    parcelCrop = models.ForeignKey('SmartSaha.ParcelCrop', on_delete=models.SET_NULL, null=True, blank=True)
    forecast_date = models.DateField()  # date pour laquelle on prévoit le rendement
    predicted_yield = models.FloatField()  # rendement prévu par hectare
    created_at = models.DateTimeField(auto_now_add=True)


    class Meta:
        unique_together = ("parcelCrop", "forecast_date")
        ordering = ['forecast_date']
    def __str__(self):
        return f"{self.parcelCrop.parcel.parcel_name} - {self.forecast_date} - {self.predicted_yield:.2f} kg/ha"