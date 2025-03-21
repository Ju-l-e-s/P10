from django.core.cache import cache

class CacheInvalidationMixin:
    """
    Mixin to automatically invalidate the cache after create, update, or delete operations.

    **How to use:**

        from rest_framework.viewsets import ModelViewSet
        from .mixins import CacheInvalidationMixin
        from .models import Project
        from .serializers import ProjectSerializer

        class ProjectViewSet(CacheInvalidationMixin, ModelViewSet):
            queryset = Project.objects.all()
            serializer_class = ProjectSerializer


    :ivar cache: The Django cache instance used for storage.
    """

    def create(self, request, *args, **kwargs):
        """
        Creates a new object and invalidates the cache.

        :param request: The request instance containing user data and payload.
        :type request: rest_framework.request.Request
        :return: The response containing the created object.
        :rtype: rest_framework.response.Response
        """
        response = super().create(request, *args, **kwargs)
        cache.clear()  # Clears cache after object creation
        return response

    def update(self, request, *args, **kwargs):
        """
        Updates an existing object and invalidates the cache.

        :param request: The request instance with update data.
        :type request: rest_framework.request.Request
        :return: The response containing the updated object.
        :rtype: rest_framework.response.Response
        """
        response = super().update(request, *args, **kwargs)
        cache.clear()  # Clears cache after object update
        return response

    def destroy(self, request, *args, **kwargs):
        """
        Deletes an object and invalidates the cache.

        :param request: The request instance targeting an object for deletion.
        :type request: rest_framework.request.Request
        :return: The response confirming deletion.
        :rtype: rest_framework.response.Response
        """
        response = super().destroy(request, *args, **kwargs)
        cache.clear()  # Clears cache after object deletion
        return response
