from django.core.cache import cache
from rest_framework.response import Response
from django.conf import settings

class CacheListMixin:
    """
        Mixin to cache list responses using an explicit cache key.

        The view define the 'cache_key' attribute.
        """
    cache_key = None

    def list(self, request, *args, **kwargs):
        if self.cache_key is None:
            return super().list(request, *args, **kwargs)
        cached_data = cache.get(self.cache_key)
        if cached_data is not None:
            return Response(cached_data)
        response = super().list(request, *args, **kwargs)
        cache.set(self.cache_key, response.data, timeout=settings.CACHE_TIMEOUT)
        return response
