from django.db import migrations

def seed_varieties(apps, schema_editor):
    Variety = apps.get_model("SmartSaha", "Variety")
    varieties = [
        {"name": "IR64 Rice", "description": "Highly cultivated rice variety in Asia, short cycle."},
        {"name": "Yellow Hybrid Corn", "description": "Resistant corn with good yield."},
        {"name": "Traditional Cassava", "description": "Basic food crop, edible tubers."},
        {"name": "Roma Tomato", "description": "Resistant tomato, used for sauces and canning."},
        {"name": "Green Bean", "description": "Protein-rich legume, fast-growing."},
        {"name": "Tropical Soybean", "description": "Oilseed legume, fixes nitrogen in the soil."},
        {"name": "Spunta Potato", "description": "Early variety, medium-sized tubers."},
        {"name": "Local Peanut", "description": "Oilseed plant cultivated for its seeds."},
        {"name": "Sugarcane", "description": "Industrial crop for sugar production."},
        {"name": "Arabica Coffee", "description": "Cash crop, aromatic coffee beans."},
        {"name": "Wheat Durum", "description": "Hard wheat variety for pasta and bread."},
        {"name": "Barley", "description": "Cereal crop used for food, fodder, and brewing."},
        {"name": "Sunflower", "description": "Oilseed crop, high-quality edible oil."},
        {"name": "Cabbage", "description": "Leafy vegetable, short cycle, widely consumed."},
        {"name": "Onion", "description": "Bulb vegetable, staple in cooking."},
        {"name": "Garlic", "description": "Bulb vegetable, used for flavoring."},
        {"name": "Chili Pepper", "description": "Spicy vegetable, widely used in sauces."},
        {"name": "Cocoa", "description": "Cash crop, used for chocolate production."},
        {"name": "Vanilla", "description": "Aromatic crop, high-value spice."},
        {"name": "Coconut", "description": "Tropical crop, multiple uses: oil, water, copra."}
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
