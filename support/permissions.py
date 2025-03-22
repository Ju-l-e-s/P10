from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.request import Request
from rest_framework.views import APIView
from .models import Contributor, Project

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
        # Allow authenticated users to read (GET)
        if view.action in ["list", "retrieve"]:
            return request.user.is_authenticated

        # Extract project_id from request data or URL kwargs
        project_id = request.data.get("project") or view.kwargs.get("project_pk") or view.kwargs.get("pk")

        # Check if the authenticated user is the author of the project
        if project_id:
            return Project.objects.filter(id=project_id, author=request.user).exists()

        return False


class IsContributor(BasePermission):
    """
    Permission that ensures the user is a **contributor** of a project before accessing its resources.

    This is used to **restrict access** to projects, issues, and comments to **only contributors**.

    **Logic:**
    - If the request is to **list projects**, the user just needs to be authenticated.
    - If the request is to **modify** something, the user must be a contributor of the related project.

    :ivar message: Error message returned when the permission is denied.
    :vartype message: str
    """

    message = "You must be a contributor to this project."

    def has_permission(self, request, view):
        """
        Checks if the request user is a contributor to the project.
        For detail views (retrieve, update, destroy), defers to object-level permissions.

        :param request: The incoming HTTP request.
        :type request: rest_framework.request.Request
        :param view: The view handling the request.
        :type view: rest_framework.views.APIView
        :return: True if allowed, otherwise False.
        :rtype: bool
        """
        # For list action, require authentication.
        if view.action == "list":
            return request.user.is_authenticated

        # For create action, try to get the project ID from request.data.
        if view.action == "create":
            project_id = request.data.get("project")
            # If project_id is not provided, check if an issue is provided.
            if not project_id:
                issue_id = request.data.get("issue")
                if issue_id:
                    from .models import Issue
                    try:
                        project_id = Issue.objects.get(id=issue_id).project_id
                    except Issue.DoesNotExist:
                        return False
                else:
                    return False
            return Contributor.objects.filter(user=request.user, project_id=project_id).exists()

        # For other actions, defer to object-level permissions.
        return True

    def has_object_permission(self, request, view, obj):
        """
        Checks object-level permission to determine if the request user is a contributor to the project.
        Also allows the action if the user is the author of the object.

        :param request: The incoming HTTP request.
        :type request: rest_framework.request.Request
        :param view: The view handling the request.
        :type view: rest_framework.views.APIView
        :param obj: The object being accessed (e.g., Comment).
        :type obj: object
        :return: True if allowed, otherwise False.
        :rtype: bool
        """
        # Allow if the user is the author of the object (compare by id).
        if hasattr(obj, "author") and obj.author and request.user and (obj.author.id == request.user.id):
            return True

        # Determine the project id from the object.
        if hasattr(obj, "project"):
            project_id = obj.project.id
        elif hasattr(obj, "issue"):
            project_id = obj.issue.project.id
        else:
            return False

        return Contributor.objects.filter(user=request.user, project_id=project_id).exists()

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
