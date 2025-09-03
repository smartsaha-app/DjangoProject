from django.db import migrations

def seed_task_data(apps, schema_editor):
    TaskStatus = apps.get_model("SmartSaha", "TaskStatus")
    TaskPriority = apps.get_model("SmartSaha", "TaskPriority")

    statuses = [
        {"name": "Pending", "description": "Tâche en attente"},
        {"name": "In Progress", "description": "Tâche en cours"},
        {"name": "Done", "description": "Tâche terminée"},
        {"name": "Cancelled", "description": "Tâche annulée"},
    ]

    for status in statuses:
        TaskStatus.objects.get_or_create(name=status["name"], defaults={"description": status["description"]})

    priorities = [
        {"name": "High", "description": "Très urgent"},
        {"name": "Medium", "description": "Normal"},
        {"name": "Low", "description": "Peut attendre"},
    ]

    for priority in priorities:
        TaskPriority.objects.get_or_create(name=priority["name"], defaults={"description": priority["description"]})


def unseed_task_data(apps, schema_editor):
    TaskStatus = apps.get_model("SmartSaha", "TaskStatus")
    TaskPriority = apps.get_model("SmartSaha", "TaskPriority")

    TaskStatus.objects.all().delete()
    TaskPriority.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("SmartSaha", "0007_remove_task_user"),  # ajuste avec le nom de la dernière migration
    ]

    operations = [
        migrations.RunPython(seed_task_data, unseed_task_data),
    ]
