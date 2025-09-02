from django.db import models
# -------------------------------
# Cultures
# -------------------------------
class Crop(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    variety = models.ForeignKey('SmartSaha.Variety', on_delete=models.SET_NULL, null=True, blank=True)
    planting_date = models.DateField()
    harvest_date = models.DateField(null=True, blank=True)
    area = models.FloatField()
    status = models.ForeignKey('SmartSaha.StatusCrop', on_delete=models.SET_NULL, null=True, blank=True)  # ex: planted, growing, harvested
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey('SmartSaha.User', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return  f"{self.name} - {self.variety.name}"

    def __init__(self):
        super().__init__()

class StatusCrop (models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.name

    def __init__(self):
        super().__init__()

class Variety(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.name

    def __init__(self):
        super().__init__()