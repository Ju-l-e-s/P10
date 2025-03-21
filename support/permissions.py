from rest_framework import permissions
from .models import Contributor, Project


class IsProjectAuthor(permissions.BasePermission):
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


class IsContributor(permissions.BasePermission):
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

        :param request: The incoming HTTP request.
        :type request: rest_framework.request.Request
        :param view: The view handling the request.
        :type view: rest_framework.views.APIView
        :return: `True` if the user is a contributor, otherwise `False`.
        :rtype: bool
        """
        # Allow authenticated users to list projects
        if view.action == "list":
            return request.user.is_authenticated

        # Retrieve project_id from request data or URL kwargs
        project_id = request.data.get("project") or view.kwargs.get("project_pk") or view.kwargs.get("pk")

        # Handle cases where the resource is related to an issue or a comment
        if not project_id:
            issue_id = request.data.get("issue")
            if issue_id:
                # Import locally to avoid circular dependency
                from .models import Issue
                try:
                    project_id = Issue.objects.get(id=issue_id).project_id
                except Issue.DoesNotExist:
                    return False

        # Check if the user is a contributor to the project
        if project_id:
            return Contributor.objects.filter(user=request.user, project_id=project_id).exists()

        return False


class IsResourceAuthorOrReadOnly(permissions.BasePermission):
    """
    Ensures that only the **author** of a resource (Issue or Comment) can modify or delete it.

    - **Read access** (`GET`): Allowed for everyone.
    - **Modification** (`PUT`, `PATCH`, `DELETE`): Only the **author** of the resource can modify or delete it.

    This prevents other contributors from altering resources they didn’t create.

    :ivar message: Error message returned when the permission is denied.
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
        :return: `True` if the request method is safe or the user is the author, otherwise `False`.
        :rtype: bool
        """
        # Allow read-only requests
        if request.method in permissions.SAFE_METHODS:
            return True

        # Only allow modifications if the user is the author
        return obj.author == request.user
