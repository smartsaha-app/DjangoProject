# SmartSaha/management/commands/yield_analytics.py
from django.core.management.base import BaseCommand

from SmartSaha.services import YieldAnalyticsService


class Command(BaseCommand):
    help = "Génère des statistiques et graphiques sur les rendements"

    def handle(self, *args, **options):
        service = YieldAnalyticsService()
        files = service.run_all(save_dir="reports")
        if not files:
            self.stdout.write(self.style.WARNING("Aucune donnée disponible."))
        else:
            self.stdout.write(self.style.SUCCESS(f"Graphiques générés : {files}"))
