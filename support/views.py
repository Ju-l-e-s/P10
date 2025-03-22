from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.conf import settings
from .models import User, Project, Contributor, Issue, Comment
from .serializers import (
    UserSerializer, ProjectSerializer, ContributorSerializer,
    IssueSerializer, CommentSerializer
)
from .permissions import IsProjectAuthor, IsContributor, IsResourceAuthorOrReadOnly, IsSelfOrCreateOnly
from .mixins import CacheListMixin

CACHE_TIMEOUT = settings.CACHE_TIMEOUT  # Cache duration: 5 minutes

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing users.

    Provides standard CRUD operations for user management.

    :cvar queryset: The base queryset containing all users.
    :cvar serializer_class: The serializer used to convert User objects into JSON.
    :cvar permission_classes: Permissions required to access this view.

    **Permissions:**
        - Requires authentication.
        - Allows users to retrieve, create, update, and delete their own accounts.

    **Endpoints:**
        - `GET /api/users/{id}` → current user info
        - `POST /api/users/` → Create a new user
        - `PATCH /api/users/{id}/` → Update user data
        - `DELETE /api/users/{id}/` → Delete user

    **Example Usage :**
    GET http://127.0.0.1:8000/api/users/ -H "Authorization: Bearer <token>"
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsSelfOrCreateOnly]
    http_method_names = ["get", "post", "patch", "delete"]

    def get_queryset(self):
        if self.request.user and self.request.user.is_authenticated:
            return User.objects.filter(id=self.request.user.id)
        return User.objects.none()


@method_decorator(cache_page(CACHE_TIMEOUT), name="dispatch")
class ProjectViewSet(CacheListMixin, viewsets.ModelViewSet):
    """
    API endpoint for managing projects.

    **Permissions:**
        - Users can create projects.
        - Users can retrieve projects they authored or contributed to.
        - Only the project author can update or delete a project.

    **Caching:**
        - Responses are cached for 5 minutes to improve performance.

    :cvar serializer_class: The serializer used to convert Project objects into JSON.
    :cvar permission_classes: Required permissions to access this view.
    :ivar request: The request instance containing user authentication data.

    **Endpoints:**
        - `GET /api/projects/` → List all accessible projects
        - `POST /api/projects/` → Create a new project
        - `PUT /api/projects/{id}/` → Update a project (Author only)
        - `DELETE /api/projects/{id}/` → Delete a project (Author only)

    **Example Usage (Python requests):**

        import requests
        headers = {"Authorization": "Bearer <token>"}
        response = requests.get("http://127.0.0.1:8000/api/projects/", headers=headers)
        print(response.json())
    """
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "put", "patch", "delete"]
    cache_key = "projects_list"  # Explicit cache key for projects list

    def get_queryset(self):
        return (
            Project.objects
            .select_related("author")
            .prefetch_related("contributors")
            .filter(
                Q(author=self.request.user)
                | Q(contributors__user=self.request.user)
            ).distinct().order_by("id")
        )


@method_decorator(cache_page(CACHE_TIMEOUT), name="dispatch")
class ContributorViewSet(CacheListMixin, viewsets.ModelViewSet):
    """
    API endpoint for managing project contributors.

    **Permissions:**
        - Users can retrieve contributors of their projects.
        - Project authors can add and remove contributors.

    **Caching:**
        - Responses are cached for 5 minutes.

    :cvar serializer_class: The serializer used to convert Contributor objects into JSON.
    :cvar permission_classes: Required permissions to access this view.
    :ivar request: The request instance containing user authentication data.

    **Endpoints:**
        - `GET /api/contributors/` → List all contributors
        - `POST /api/contributors/` → Add a contributor
        - `DELETE /api/contributors/{id}/` → Remove a contributor

    **Example Usage (cURL):**

        curl -X GET http://127.0.0.1:8000/api/contributors/ -H "Authorization: Bearer <token>"
    """
    serializer_class = ContributorSerializer
    permission_classes = [IsAuthenticated, IsProjectAuthor]
    http_method_names = ["get", "post", "patch", "delete"]
    cache_key = "contributors_list"  # Explicit cache key for contributors list

    def get_queryset(self):
        return (
            Contributor.objects
            .select_related("user", "project")
            .filter(project__author=self.request.user).order_by("id")
        )


@method_decorator(cache_page(CACHE_TIMEOUT), name="dispatch")
class IssueViewSet(CacheListMixin, viewsets.ModelViewSet):
    """
    API endpoint for managing issues.

    **Permissions:**
        - Users can create issues in projects they contribute to.
        - Users can retrieve, update, or delete their own issues.

    **Caching:**
        - Responses are cached for 5 minutes.

    :cvar serializer_class: The serializer used to convert Issue objects into JSON.
    :cvar permission_classes: Required permissions to access this view.
    :ivar request: The request instance containing user authentication data.

    **Endpoints:**
        - `GET /api/issues/` → List all issues
        - `POST /api/issues/` → Create an issue
        - `PUT /api/issues/{id}/` → Update an issue (Author only)
        - `DELETE /api/issues/{id}/` → Delete an issue (Author only)
    """
    serializer_class = IssueSerializer
    permission_classes = [IsAuthenticated, IsContributor, IsResourceAuthorOrReadOnly]
    http_method_names = ["get", "post", "put", "patch", "delete"]
    cache_key = "issues_list"  # Explicit cache key for issues list

    def get_queryset(self):
        return (
            Issue.objects
            .select_related("project", "author", "assignee")
            .prefetch_related("comments")
            .filter(
                project__contributors__user=self.request.user
            ).distinct().order_by("id")
        )


@method_decorator(cache_page(CACHE_TIMEOUT), name="dispatch")
class CommentViewSet(CacheListMixin, viewsets.ModelViewSet):
    """
    API endpoint for managing comments on issues.

    Users can:
    - Create comments on issues within projects they contribute to.
    - Retrieve comments related to issues in contributed projects.
    - Update or delete their own comments.

    Implements caching to optimize query performance.

    :cvar serializer_class: The serializer used to convert Comment objects into JSON.
    :cvar permission_classes: Required permissions to access this view.
    :ivar request: The request instance containing user authentication data.
    """
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsContributor, IsResourceAuthorOrReadOnly]
    http_method_names = ["get", "post", "put", "patch", "delete"]
    cache_key = "comments_list"  # Explicit cache key for comments list

    def get_queryset(self):
        return Comment.objects \
            .select_related("issue", "author") \
            .filter(
                issue__project__contributors__user=self.request.user
            ).distinct().order_by("id")
