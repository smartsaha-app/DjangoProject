from django.db import models
import uuid

# -------------------------------
# Parcelles
# -------------------------------
class Parcel(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey('SmartSaha.User', on_delete=models.CASCADE)
    parcel_name = models.CharField(max_length=255)
    # Stockage des points du polygone sous forme de liste JSON [{"lat":.., "lng":..}, ...]
    points = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.parcel_name} - {self.owner.username} "



    def add_point(self, lat, lng, order):
        self.points.append({"lat": lat, "lng": lng, "order": order})
        self.save()

    def get_polygon(self):
        # Retourne le polygone formaté
        return [(p["lat"], p["lng"]) for p in sorted(self.points, key=lambda x: x["order"])]
# -------------------------------
# Points de parcelle (optionnel)
# -------------------------------
class ParcelPoint(models.Model):
    parcel = models.ForeignKey(Parcel, on_delete=models.CASCADE, related_name='parcel_points')
    latitude = models.FloatField()
    longitude = models.FloatField()
    order = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.parcel.parcel_name} - {self.order}"



    class Meta:
        ordering = ['order']
