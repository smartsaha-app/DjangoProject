from django.db import migrations

def seed_status_crop(apps, schema_editor):
    StatusCrop = apps.get_model("SmartSaha", "StatusCrop")
    statuses = [
        {"name": "Planned", "description": "Culture planifiée mais pas encore plantée"},
        {"name": "Planted", "description": "Semis ou plantation effectuée"},
        {"name": "Germinated", "description": "Début de la germination / jeunes pousses"},
        {"name": "Growing", "description": "Culture en phase de croissance"},
        {"name": "Flowering", "description": "Plantes en floraison"},
        {"name": "Fruiting", "description": "Formation et développement des fruits"},
        {"name": "Mature", "description": "Prête à être récoltée"},
        {"name": "Harvested", "description": "Culture récoltée"},
        {"name": "Post-Harvest", "description": "Résidus ou terrain en repos après récolte"},
        {"name": "Failed", "description": "Culture perdue (maladie, sécheresse, etc.)"},
    ]

    for status in statuses:
        StatusCrop.objects.get_or_create(name=status["name"], defaults={"description": status["description"]})

def unseed_status_crop(apps, schema_editor):
    StatusCrop = apps.get_model("SmartSaha", "StatusCrop")
    StatusCrop.objects.all().delete()

class Migration(migrations.Migration):

    dependencies = [
        ('SmartSaha', '0004_remove_crop_area_remove_crop_harvest_date_and_more'),
    ]

    operations = [
        migrations.RunPython(seed_status_crop, reverse_code=unseed_status_crop),
    ]
