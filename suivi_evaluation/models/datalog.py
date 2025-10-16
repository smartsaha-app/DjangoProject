from django.db import models
from django.contrib.auth import get_user_model
import uuid
User = get_user_model()


class DataLog(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=50, choices=[
        ('ADD', 'Ajout'),
        ('EDIT', 'Modification'),
        ('DELETE', 'Suppression')
    ])
    table_name = models.CharField(max_length=100)
    record_id = models.CharField(max_length=100)
    field = models.CharField(max_length=100)
    old_value = models.TextField(blank=True, null=True)
    new_value = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class CustomField(models.Model):
    FIELD_TYPES = [
        ("text", "Text"),
        ("number", "Number"),
        ("date", "Date"),
        ("boolean", "Boolean"),
    ]
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    field_type = models.CharField(max_length=50, choices=FIELD_TYPES)
    table_target = models.CharField(max_length=100)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


class CustomFieldValue(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    custom_field = models.ForeignKey(CustomField, on_delete=models.CASCADE)
    record_id = models.CharField(max_length=100)
    value = models.TextField()

