from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from SmartSaha.models import Parcel, ParcelCrop, YieldRecord, YieldForecast, Task, SoilData, ClimateData


def invalidate_dashboard_cache(user_id):
    cache_key = f"dashboard_full_{user_id}"
    cache.delete(cache_key)

@receiver([post_save, post_delete], sender=Parcel)
def clear_dashboard_cache_parcel(sender, instance, **kwargs):
    if instance.owner_id:
        invalidate_dashboard_cache(instance.owner_id)

@receiver([post_save, post_delete], sender=ParcelCrop)
def clear_dashboard_cache_parcelcrop(sender, instance, **kwargs):
    if instance.parcel.owner_id:
        invalidate_dashboard_cache(instance.parcel.owner_id)

@receiver([post_save, post_delete], sender=YieldRecord)
def clear_dashboard_cache_yield(sender, instance, **kwargs):
    if instance.parcelCrop.parcel.owner_id:
        invalidate_dashboard_cache(instance.parcelCrop.parcel.owner_id)

@receiver([post_save, post_delete], sender=YieldForecast)
def clear_dashboard_cache_forecast(sender, instance, **kwargs):
    if instance.parcelCrop.parcel.owner_id:
        invalidate_dashboard_cache(instance.parcelCrop.parcel.owner_id)


def invalidate_user_dashboard(instance):
    user = None
    if hasattr(instance, "owner"):
        user = instance.owner
    elif hasattr(instance, "parcel") and instance.parcel.owner:
        user = instance.parcel.owner
    elif hasattr(instance, "parcelCrop") and instance.parcelCrop.parcel.owner:
        user = instance.parcelCrop.parcel.owner

    if user:
        cache.delete(f"dashboard_{user.id}")

@receiver([post_save, post_delete], sender=Parcel)
@receiver([post_save, post_delete], sender=ParcelCrop)
@receiver([post_save, post_delete], sender=YieldRecord)
@receiver([post_save, post_delete], sender=Task)
@receiver([post_save, post_delete], sender=SoilData)
@receiver([post_save, post_delete], sender=ClimateData)

def invalidate_cache_on_change(sender, instance, **kwargs):
    invalidate_user_dashboard(instance)