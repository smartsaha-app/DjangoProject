from django.db import models
import uuid

# -------------------------------
# Publications / Marketplace
# -------------------------------
class Post(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey('SmartSaha.User', on_delete=models.SET_NULL, null=True)
    crop = models.ForeignKey('SmartSaha.Crop', on_delete=models.SET_NULL, null=True)
    quantitykg = models.DecimalField(max_digits=12, decimal_places=2)
    pricekg = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.ForeignKey('SmartSaha.PostCurrency', on_delete=models.SET_NULL, null=True)
    location = models.TextField()
    description = models.TextField(null=True, blank=True)
    type = models.ForeignKey('SmartSaha.PostType', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    uuid_post = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

class PostType (models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField()

class PostCurrency (models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField()