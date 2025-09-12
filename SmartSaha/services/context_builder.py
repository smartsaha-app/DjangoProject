# services/context_builder.py
from SmartSaha.models import Parcel
from SmartSaha.services import ParcelDataService
import asyncio

class ContextBuilder:

    @staticmethod
    def build_context(parcel_uuid=None, user_modules=None):
        """
        Construit le contexte complet pour l'assistant agronome.
        user_modules = {
            "parcel": True/False,
            "soil": True/False,
            "weather": True/False,
            "crops": True/False,
            "yield_records": True/False
        }
        """
        user_modules = user_modules or {}
        context = []

        parcel = None
        if parcel_uuid:
            try:
                parcel = Parcel.objects.get(uuid=parcel_uuid)
                if user_modules.get("parcel", False):
                    context.append(f"Parcelle: {parcel.parcel_name}")
            except Parcel.DoesNotExist:
                context.append("Parcelle inconnue")

        # Sol et Climat (synchrone)
        if parcel and user_modules.get("soil", False):
            soil_info = ParcelDataService.fetch_soil(parcel)  # doit être synchrone
            if soil_info:
                context.append(soil_info)

        if parcel and user_modules.get("weather", False):
            climate_info = ParcelDataService.fetch_climate(parcel)  # doit être synchrone
            if climate_info:
                context.append(climate_info)

        # Cultures et tâches
        if parcel and user_modules.get("crops", False):
            parcel_crops_info = ParcelDataService.build_parcel_crops(parcel)
            context.append(f"Cultures et tâches: {parcel_crops_info}")

        # Rendements
        if parcel and user_modules.get("yield_records", False):
            yields_info = ParcelDataService.build_yield_records(parcel)
            context.append(f"Historique rendements: {yields_info}")

        return "\n".join([str(c) for c in context])
