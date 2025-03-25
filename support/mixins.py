import logging
from django.core.cache import cache
from rest_framework.response import Response

logger = logging.getLogger(__name__)

class CacheListMixin:
    """
    Caching mixin for DRF ViewSets.
    Use a version per user and endpoint to invalidate all pages.
    """
    cache_key = None  # difine in each ViewSet

    def get_cache_version(self, request):
        """Retrieve or initialize the cache version for the user and endpoint"""
        if self.cache_key and request.user.is_authenticated:
            version_key = f"{self.cache_key}_version_user_{request.user.pk}"
            version = cache.get(version_key)
            if not version:
                version = 1
                cache.set(version_key, version, None)
            return version
        return 1

    def get_cache_key(self, request):
        """Generate a cache key including the user, the page number and the version"""
        if self.cache_key and request.user.is_authenticated:
            page = request.query_params.get('page', '1')
            version = self.get_cache_version(request)
            return f"{self.cache_key}_user_{request.user.pk}_page_{page}_v{version}"
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
        """Centralized cache invalidation mechanism for all existing pages"""
        if self.cache_key and self.request.user.is_authenticated:
            version_key = f"{self.cache_key}_version_user_{self.request.user.pk}"
            version = cache.get(version_key) or 1
            cache.set(version_key, version + 1, None)
            logger.debug(f"Cache invalidated: {version_key} incremented to {version + 1}")
