from django.db import models

# -------------------------------
# Tâches / Suivi
# -------------------------------
class Task(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    crop = models.ForeignKey('SmartSaha.Crop', on_delete=models.SET_NULL, null=True, blank=True)
    due_date = models.DateField()
    priority = models.ForeignKey('SmartSaha.TaskPriority', on_delete=models.SET_NULL, null=True, blank=True) # ex: high, medium, low
    status = models.ForeignKey('SmartSaha.TaskStatus', on_delete=models.SET_NULL, null=True, blank=True)    # ex: pending, done
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.crop.parcel_name} - {self.due_date} - {self.priority.name} - {self.status.name}"

class TaskPriority (models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.name



class TaskStatus (models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.name

