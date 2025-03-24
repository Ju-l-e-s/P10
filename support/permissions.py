from django.db.models import Q
from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.request import Request
from rest_framework.views import APIView
from .models import Contributor, Project, Issue, Comment



class IsSelfOrCreateOnly(BasePermission):
    """
    Allows unauthenticated users to create an account (create action),
    and once authenticated, permits users to access (retrieve, update, delete) only their own account.
    """
    message = "You can only access your own account."

    def has_permission(self, request: Request, view: APIView) -> bool:
        """
        Checks if the request has general permission to perform the action at the view level.

        :param request: The incoming HTTP request.
        :type request: rest_framework.request.Request
        :param view: The view handling the request.
        :type view: rest_framework.views.APIView
        :return: True if the action is allowed, otherwise False.
        :rtype: bool
        """
        if getattr(view, 'action', None) == "create":
            return True
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request: Request, view: APIView, obj) -> bool:
        """
        Checks if the request user is allowed to access the specific object.

        :param request: The incoming HTTP request.
        :type request: rest_framework.request.Request
        :param view: The view handling the request.
        :type view: rest_framework.views.APIView
        :param obj: The object being accessed (expected to be a User instance).
        :type obj: Any
        :return: True if the object belongs to the requesting user, otherwise False.
        :rtype: bool
        """
        return obj == request.user


class IsProjectAuthor(BasePermission):
    """
    Custom permission that allows only the **author** of a project to perform certain actions.

    This permission is mainly used for **creating** and **deleting** contributors in `ContributorViewSet`.

    **Logic:**
    - If the user is making a **read-only request** (`list`, `retrieve`), they just need to be authenticated.
    - For **modification** (`POST`, `DELETE`), the user must be **the author of the project**.

    :ivar message: Error message returned when the permission is denied.
    :vartype message: str
    """

    message = "Only the project author can perform this action."

    def has_permission(self, request, view):
        """
        Checks if the request user is the author of the project.

        :param request: The incoming HTTP request.
        :type request: rest_framework.request.Request
        :param view: The view handling the request.
        :type view: rest_framework.views.APIView
        :return: `True` if the user is the project author, otherwise `False`.
        :rtype: bool
        """
        if view.action in ["list", "retrieve"]:
            return request.user.is_authenticated

            # If the user tries to delete a contributor
        if view.action == "destroy" and "pk" in view.kwargs:
            try:
                contributor = Contributor.objects.get(pk=view.kwargs["pk"])
            except Contributor.DoesNotExist:
                return False
            # check if the user is the project author
            return contributor.project.author == request.user

        project_id = request.data.get("project") or view.kwargs.get("project_pk") or view.kwargs.get("pk")
        if project_id:
            return Project.objects.filter(id=project_id, author=request.user).exists()

        return False


class IsContributor(BasePermission):
    """
    Permission ensuring the user is a contributor to the project before accessing its resources.
    Used to restrict access to projects, issues, and comments to only contributors.

    **Logic:**
    - If the request is to list resources (GET), the user must be authenticated.
    - To create (POST), update (PATCH), or delete (DELETE) resources,
      the user must be a contributor or the author of the relevant project.
    """

    message = "You must be a contributor to this project."

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return request.user.is_authenticated

        project_id = None

        if view.action == "create":
            # Try to get first the project_id from the request
            project_id = request.data.get("project")

            # if not project_id is given we try to get it from the issue
            if not project_id:
                issue_id = request.data.get("issue")
                if issue_id:
                    try:
                        issue = Issue.objects.select_related("project").get(id=issue_id)
                        project_id = issue.project_id
                    except Issue.DoesNotExist:
                        return False
                else:
                    return False

        elif view.action in ["partial_update", "destroy"]:
            obj = view.get_object()
            project = self._get_project_from_obj(obj)
            if project:
                project_id = project.id
            else:
                return False
        else:
            return False

        return Contributor.objects.filter(
            Q(project_id=project_id) &
            (Q(user=request.user) | Q(project__author=request.user))
        ).exists()

    def has_object_permission(self, request, view, obj):
        project = self._get_project_from_obj(obj)

        # For write actions, only the project author is allowed
        if request.method not in SAFE_METHODS:
            return project and project.author == request.user

        # For readind, the user must be a contributor to the project
        return Contributor.objects.filter(user=request.user, project=project).exists()

    def _get_project_from_obj(self, obj):
        if isinstance(obj, Project):
            return obj
        if isinstance(obj, (Issue, Contributor)):
            return obj.project
        if isinstance(obj, Comment):
            return obj.issue.project
        return None


class IsResourceAuthorOrReadOnly(BasePermission):
    """
    Ensures that only the author of a resource (Issue or Comment) can modify or delete it.

    - Read access (GET): Allowed for everyone.
    - Modification (PUT, PATCH, DELETE): Only the author can modify or delete the resource.

    :ivar message: Error message returned when permission is denied.
    :vartype message: str
    """
    message = "Only the resource author can modify or delete."

    def has_object_permission(self, request, view, obj):
        """
        Checks if the request user is the author of the object.

        :param request: The incoming HTTP request.
        :type request: rest_framework.request.Request
        :param view: The view handling the request.
        :type view: rest_framework.views.APIView
        :param obj: The object being accessed.
        :type obj: Issue or Comment
        :return: True if the request method is safe or the user is the author, otherwise False.
        :rtype: bool
        """
        # Allow read-only requests.
        if request.method in SAFE_METHODS:
            return True

        # Only allow modifications if the user is the author.
        return obj.author == request.user


class IsProjectAuthorForContributor(BasePermission):
    message = "Only the project author can modify or delete contributors."

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return request.user.is_authenticated

        # For create, the project id must be provided and the user must be the author
        if view.action == "create":
            project_id = request.data.get("project")
            if project_id:
                return Project.objects.filter(id=project_id, author=request.user).exists()
            return False

        # For update/delete, we check on the object
        if view.action in ["partial_update", "destroy"]:
            obj = view.get_object()
            project = self._get_project_from_obj(obj)
            if project:
                return project.author == request.user
            return False

        return False

    def _get_project_from_obj(self, obj):
        if hasattr(obj, "project"):
            return obj.project
        return None
