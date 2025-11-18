# agriculture/management/commands/collect_weather_data.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from SmartSaha.models import Parcel
from SmartSaha.services import WeatherDataCollector
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Collecte automatiquement les données météo pour toutes les parcelles'

    def add_arguments(self, parser):
        parser.add_argument(
            '--parcel-id',
            type=int,
            help='ID spécifique d une parcelle à mettre à jour'
        )

    def handle(self, *args, **options):
        self.stdout.write('Début de la collecte des données météo...')

        collector = WeatherDataCollector()
        parcel_id = options.get('parcel_id')

        if parcel_id:
            # Collecte pour une parcelle spécifique
            try:
                parcel = Parcel.objects.get(id=parcel_id)
                if parcel.latitude and parcel.longitude:
                    result = collector.collect_and_save_weather_data(
                        parcel, parcel.latitude, parcel.longitude
                    )
                    if result['success']:
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'✅ Données collectées pour {parcel.name}: '
                                f"{result['alerts_generated']} alertes"
                            )
                        )
                    else:
                        self.stdout.write(
                            self.style.ERROR(
                                f'❌ Erreur pour {parcel.name}: {result["error"]}'
                            )
                        )
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f'⚠️ Parcelle {parcel.name} sans coordonnées GPS'
                        )
                    )
            except Parcel.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Parcelle {parcel_id} non trouvée')
                )
        else:
            # Collecte pour toutes les parcelles
            parcels = Parcel.objects.filter(
                latitude__isnull=False,
                longitude__isnull=False
            )

            total = parcels.count()
            success_count = 0

            for parcel in parcels:
                result = collector.collect_and_save_weather_data(
                    parcel, parcel.latitude, parcel.longitude
                )

                if result['success']:
                    success_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✅ {parcel.name}: {result["alerts_generated"]} alertes'
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(
                            f'❌ {parcel.name}: {result["error"]}'
                        )
                    )

            self.stdout.write(
                self.style.SUCCESS(
                    f'Collecte terminée: {success_count}/{total} parcelles mises à jour'
                )
            )