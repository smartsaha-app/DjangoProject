from django.db import models



# -------------------------------
# Cultures
# -------------------------------
class Crop(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    variety = models.ForeignKey('SmartSaha.Variety', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return  f"{self.name} - {self.variety.name}"



class StatusCrop (models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.name



class Variety(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.name


class ParcelCrop(models.Model):
    parcel = models.ForeignKey('SmartSaha.Parcel', on_delete=models.CASCADE, related_name='parcel_crops')
    crop = models.ForeignKey('SmartSaha.Crop', on_delete=models.CASCADE)
    planting_date = models.DateField()
    harvest_date = models.DateField(null=True, blank=True)
    area = models.FloatField()
    status = models.ForeignKey('SmartSaha.StatusCrop', on_delete=models.SET_NULL, null=True,blank=True)  # ex: planted, growing, harvested
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.parcel.parcel_name} - {self.crop.name} - {self.status.name} - {self.area} - {self.created_at} - {self.harvest_date}"