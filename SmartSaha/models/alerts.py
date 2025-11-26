from django.db import models

from SmartSaha.models import Parcel


# models.py
class Alert(models.Model):
    SEVERITY_CHOICES = [
        ('LOW', 'Faible'),
        ('MEDIUM', 'Moyenne'),
        ('HIGH', 'Haute'),
        ('CRITICAL', 'Critique')
    ]

    parcel = models.ForeignKey(Parcel, on_delete=models.CASCADE)
    type = models.CharField(max_length=100)
    message = models.TextField()
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES)
    action = models.TextField(blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    alert_date = models.DateField()  # Date de l'événement alerté

    class Meta:
        ordering = ['-created_at']