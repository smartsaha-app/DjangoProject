# services/data_retrieval.py
from SmartSaha.models import Parcel, Crop


def get_context_for_question(parcel_id: str = None, crop_name: str = None):
    context = []
    if parcel_id:
        try:
            parcel = Parcel.objects.get(id=parcel_id)
            context.append(f"Parcelle: {parcel.name}, Surface: {parcel.area} ha, Sol: {parcel.soil_type}")
        except Parcel.DoesNotExist:
            context.append("Parcelle: inconnue")
    if crop_name:
        crops = Crop.objects.filter(name__icontains=crop_name)
        for crop in crops:
            context.append(f"Culture: {crop.name}, Rendement moyen: {crop.yield_amount} t/ha")
    return "\n".join(context)
