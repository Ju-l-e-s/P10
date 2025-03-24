import logging
from django.core.cache import cache
from rest_framework.response import Response

logger = logging.getLogger(__name__)

class CacheListMixin:
    """
    Caching mixin for DRF ViewSets
    Handles automatic cache invalidation on data modification
    """
    cache_key = None  # defined in each ViewSets

    def get_cache_key(self, request):
        """Generate versioned cache key with user context"""
        if self.cache_key and request.user.is_authenticated:
            return f"{self.cache_key}_user_{request.user.pk}_v2"
        return None

    def list(self, request, *args, **kwargs):
        """Optimized list action with smart caching"""
        cache_key = self.get_cache_key(request)
        if not cache_key:
            return super().list(request, *args, **kwargs)

        if (cached := cache.get(cache_key)) is not None:
            logger.debug(f"Cache hit for {cache_key}")
            return Response(cached)

        logger.debug(f"Cache miss for {cache_key}")
        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, timeout=300)
        return response

    def perform_create(self, serializer):
        """Override creation with cache invalidation"""
        super().perform_create(serializer)
        self._invalidate_cache()

    def perform_partial_update(self, serializer):
        """Override update with cache invalidation"""
        super().perform_partial_update(serializer)
        self._invalidate_cache()

    def perform_destroy(self, instance):
        """Override deletion with cache invalidation"""
        super().perform_destroy(instance)
        self._invalidate_cache()

    def _invalidate_cache(self):
        """Centralized cache invalidation mechanism"""
        cache_key = self.get_cache_key(self.request)
        if cache_key:
            logger.debug(f"Invalidating cache key: {cache_key}")
            cache.delete(cache_key)
