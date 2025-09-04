from django.db import models
from django.utils import timezone


# -------------------------------
# Tâches / Suivi
# -------------------------------
class Task(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    parcelCrop = models.ForeignKey('SmartSaha.ParcelCrop', on_delete=models.SET_NULL, null=True, blank=True)
    due_date = models.DateField()
    priority = models.ForeignKey('SmartSaha.TaskPriority', on_delete=models.SET_NULL, null=True, blank=True) # ex: high, medium, low
    status = models.ForeignKey('SmartSaha.TaskStatus', on_delete=models.SET_NULL, null=True, blank=True)    # ex: pending, done
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    # Pour audit trail
    history = models.JSONField(default=list, blank=True)

    def mark_as_done(self):
        """Marquer la tâche comme terminée."""
        done_status = TaskStatus.objects.filter(name__iexact="Done").first()
        if done_status:
            self.status = done_status
            self.completed_at = timezone.now()
            self.add_history("Marked as Done")
            self.save()

    def add_history(self, action: str):
        """Ajouter une entrée à l'historique de la tâche."""
        self.history.append({
            "action": action,
            "timestamp": timezone.now().isoformat()
        })
        self.save()

    def __str__(self):
        return f"{self.name} - {self.due_date} - {self.priority.name} - {self.status.name}"

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

