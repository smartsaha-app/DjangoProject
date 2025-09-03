from django.db import migrations

def seed_varieties(apps, schema_editor):
    Variety = apps.get_model("SmartSaha", "Variety")
    varieties = [
        {"name": "Riz IR64", "description": "Variété de riz très cultivée en Asie, cycle court."},
        {"name": "Maïs Jaune Hybride", "description": "Maïs résistant avec bon rendement."},
        {"name": "Manioc Traditionnel", "description": "Culture vivrière de base, tubercules comestibles."},
        {"name": "Tomate Roma", "description": "Tomate résistante, utilisée pour sauces et conserves."},
        {"name": "Haricot Vert", "description": "Légumineuse riche en protéines, cycle rapide."},
        {"name": "Soja Tropical", "description": "Légumineuse oléagineuse, fixation d’azote dans le sol."},
        {"name": "Pomme de Terre Spunta", "description": "Variété précoce, tubercules de taille moyenne."},
        {"name": "Arachide Locale", "description": "Plante oléagineuse cultivée pour ses graines."},
        {"name": "Canne à Sucre", "description": "Culture industrielle pour production de sucre."},
        {"name": "Café Arabica", "description": "Culture de rente, grains de café aromatiques."},
    ]

    for variety in varieties:
        Variety.objects.get_or_create(
            name=variety["name"],
            defaults={"description": variety["description"]}
        )

def unseed_varieties(apps, schema_editor):
    Variety = apps.get_model("SmartSaha", "Variety")
    Variety.objects.all().delete()

class Migration(migrations.Migration):

    dependencies = [
        ('SmartSaha', '0005_seed_status_crop'),
    ]

    operations = [
        migrations.RunPython(seed_varieties, reverse_code=unseed_varieties),
    ]
