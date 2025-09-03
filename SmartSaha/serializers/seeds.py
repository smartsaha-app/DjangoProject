from SmartSaha.models import TaskStatus, TaskPriority

def run():
    # Seed TaskStatus
    statuses = [
        {"name": "Pending", "description": "Tâche en attente"},
        {"name": "In Progress", "description": "Tâche en cours"},
        {"name": "Done", "description": "Tâche terminée"},
        {"name": "Cancelled", "description": "Tâche annulée"},
    ]

    for status in statuses:
        TaskStatus.objects.get_or_create(name=status["name"], defaults={"description": status["description"]})

    # Seed TaskPriority
    priorities = [
        {"name": "High", "description": "Très urgent"},
        {"name": "Medium", "description": "Normal"},
        {"name": "Low", "description": "Peut attendre"},
    ]

    for priority in priorities:
        TaskPriority.objects.get_or_create(name=priority["name"], defaults={"description": priority["description"]})
