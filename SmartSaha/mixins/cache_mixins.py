from django.core.cache import cache
from rest_framework.response import Response

class CacheInvalidationMixin:
    """
    Mixin pour gérer le cache automatique des ViewSets DRF.
    - Cache les endpoints list et retrieve.
    - Invalide le cache sur create/update/partial_update/destroy.
    - Supporte un cache spécifique pour des objets liés (ex: Parcel).
    """
    cache_timeout = 60 * 10  # 10 minutes par défaut
    cache_prefix = None      # À définir dans chaque ViewSet
    use_object_cache = False # Si True, cache par pk pour retrieve individuel

    def get_cache_key(self, suffix):
        return f"{self.cache_prefix}:{suffix}"

    # ---------------- READ ----------------
    def list(self, request, *args, **kwargs):
        key = self.get_cache_key("list")
        data = cache.get(key)
        if data:
            return Response(data)
        response = super().list(request, *args, **kwargs)
        cache.set(key, response.data, self.cache_timeout)
        return response

    def retrieve(self, request, *args, **kwargs):
        if self.use_object_cache:
            key = self.get_cache_key(f"detail:{kwargs.get('pk')}")
            data = cache.get(key)
            if data:
                return Response(data)
            response = super().retrieve(request, *args, **kwargs)
            cache.set(key, response.data, self.cache_timeout)
            return response
        return super().retrieve(request, *args, **kwargs)

    # ---------------- WRITE ----------------
    def invalidate_cache(self, obj=None):
        """
        Supprime tout le cache lié au ViewSet.
        Si obj est fourni, supprime aussi le cache spécifique à l'objet.
        """
        # Cache global du ViewSet


        keys = cache.keys(f"{self.cache_prefix}:*")
        for k in keys:
            cache.delete(k)

        # Cache spécifique à l'objet (ex: Parcel)
        if obj and hasattr(obj, "id"):
            obj_key = self.get_cache_key(f"detail:{obj.id}")
            cache.delete(obj_key)
            # Si lié à un parcel
            if hasattr(obj, "parcel") and obj.parcel:
                parcel_key = f"parcel_full_data_{obj.parcel.id}"
                cache.delete(parcel_key)

    def perform_create(self, serializer):
        instance = serializer.save()
        self.invalidate_cache(instance)
        return instance

    def perform_update(self, serializer):
        instance = serializer.save()
        self.invalidate_cache(instance)
        return instance

    def perform_destroy(self, instance):
        self.invalidate_cache(instance)
        instance.delete()


