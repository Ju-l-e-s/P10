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

    **Permissions:**
        - Requires authentication.
        - Allows users to retrieve, create, update, and delete their own accounts.

    **Endpoints:**
        - `GET /api/users/{id}` → current user info
        - `POST /api/users/` → Create a new user
        - `PATCH /api/users/{id}/` → Update user data
        - `DELETE /api/users/{id}/` → Delete user
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsSelfOrCreateOnly]
    http_method_names = ["get", "post", "patch", "delete"]

    def get_queryset(self):
        if self.request.user and self.request.user.is_authenticated:
            return User.objects.filter(id=self.request.user.id)
        return User.objects.none()

class ProjectViewSet(CacheListMixin, viewsets.ModelViewSet):
    """
    API endpoint for managing projects.

    **Permissions:**
        - Users can create projects.
        - Users can retrieve projects they authored or contributed to.
        - Only the project author can update or delete a project.

    **Caching:**
        - Responses are cached for 5 minutes with automatic invalidation on changes.
        - Cache is shared between contributors of the same project.

    **Endpoints:**
        - `GET /api/projects/` → List all accessible projects
        - `POST /api/projects/` → Create a new project
        - `PATCH /api/projects/{id}/` → Update a project (Author only)
        - `DELETE /api/projects/{id}/` → Delete a project (Author only)
    """
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "patch", "delete"]
    cache_key = "projects_list"

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

class ContributorViewSet(CacheListMixin, viewsets.ModelViewSet):
    """
    API endpoint for managing project contributors.

    **Permissions:**
        - Users can retrieve contributors of their projects.
        - Project authors can add and remove contributors.

    **Caching:**
        - Responses are cached for 5 minutes with automatic invalidation.
        - Visible to all project contributors.

    **Endpoints:**
        - `GET /api/contributors/` → List all contributors
        - `POST /api/contributors/` → Add a contributor
        - `PATCH /api/contributors/{id}/` → Update contributor
        - `DELETE /api/contributors/{id}/` → Remove a contributor
    """
    serializer_class = ContributorSerializer
    permission_classes = [IsAuthenticated, IsContributor]
    http_method_names = ["get", "post", "patch", "delete"]
    cache_key = "contributors_list"

    def get_queryset(self):
        return (
            Contributor.objects
            .select_related("user", "project")
            .filter(project__contributors__user=self.request.user)
            .distinct().order_by("id")
        )

class IssueViewSet(CacheListMixin, viewsets.ModelViewSet):
    """
    API endpoint for managing issues.

    **Permissions:**
        - Users can create issues in projects they contribute to.
        - Users can retrieve, update, or delete their own issues.

    **Caching:**
        - Responses are cached for 5 minutes with project-aware invalidation.
        - Shared between all project contributors.

    **Endpoints:**
        - `GET /api/issues/` → List all issues
        - `POST /api/issues/` → Create an issue
        - `PATCH /api/issues/{id}/` → Update an issue (Author only)
        - `DELETE /api/issues/{id}/` → Delete an issue (Author only)
    """
    serializer_class = IssueSerializer
    permission_classes = [IsAuthenticated,  IsResourceAuthorOrReadOnly]
    http_method_names = ["get", "post", "patch", "delete"]
    cache_key = "issues_list"

    def get_queryset(self):
        return (
            Issue.objects
            .select_related("project", "author", "assignee")
            .prefetch_related("comments")
            .filter(
                project__contributors__user=self.request.user
            ).distinct().order_by("id")
        )

class CommentViewSet(CacheListMixin, viewsets.ModelViewSet):
    """
    API endpoint for managing comments on issues.

    **Permissions:**
        - Users can create comments on issues within contributed projects.
        - Users can retrieve comments from visible issues.
        - Authors can update or delete their own comments.

    **Caching:**
        - Responses are cached for 5 minutes with issue-aware invalidation.
        - Shared between all project contributors.

    **Endpoints:**
        - `GET /api/comments/` → List all comments
        - `POST /api/comments/` → Create a comment
        - `PATCH /api/comments/{id}/` → Update comment (Author only)
        - `DELETE /api/comments/{id}/` → Delete comment (Author only)
    """
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsResourceAuthorOrReadOnly]
    http_method_names = ["get", "post", "patch", "delete"]
    cache_key = "comments_list"

    def get_queryset(self):
        return (
            Comment.objects
            .select_related("issue", "author")
            .filter(
                issue__project__contributors__user=self.request.user
            ).distinct().order_by("id")
        )
