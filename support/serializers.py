from django.utils import timezone
from rest_framework import serializers
from .models import User, Project, Contributor, Issue, Comment


class BaseAuthorSerializer(serializers.ModelSerializer):
    """
    Base serializer for models requiring an author field.

    This serializer ensures that the `author` field is automatically set to the currently authenticated user.

    :cvar author: Automatically set to the request's authenticated user.
    :ivar request: The request instance containing user authentication data.

    **Usage:**
    - Used as a base class for models that require an `author` field.
    """

    author = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        abstract = True


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for user-related operations with GDPR compliance.

    **Validations:**
    - Email is required.
    - Age must be at least 15 years old (GDPR compliance).
    - Includes `can_be_contacted` and `can_data_be_shared` fields for data privacy.

    :cvar model: The Django model associated with this serializer.
    :cvar fields: The fields included in the serialized output.
    """

    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "age",
            "can_be_contacted",
            "can_data_be_shared",
            "password",
        ]

    extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep.pop("password", None)
        return rep

    def validate_age(self, value):
        """
        Ensures that the user is at least 15 years old (GDPR compliance).

        :param value: The provided age value.
        :type value: int
        :return: The validated age.
        :rtype: int
        :raises serializers.ValidationError: If age is below 15.
        """
        if value < 15:
            raise serializers.ValidationError("User must be at least 15 years old.")
        return value


class ProjectSerializer(BaseAuthorSerializer):
    """
    Serializer for project management.

    **Features:**
    - Automatically assigns the author to the project.
    - Creates a Contributor record for the author when a project is created.

    **Endpoints:**
    - `POST /api/projects/` → Create a project.
    - `GET /api/projects/{id}/` → Retrieve project details.

    **Example Usage (cURL):**
    ```bash
    curl -X POST http://127.0.0.1:8000/api/projects/ -H "Authorization: Bearer <token>" \
         -d '{"title": "New Project", "description": "Project Description", "type": "Web"}'
    ```
    """

    class Meta:
        model = Project
        fields = ["id", "title", "description", "type", "author", "created_time"]
        read_only_fields = ["id", "created_time", "author"]

    def create(self, validated_data):
        request = self.context.get("request", None)
        if request and hasattr(request, "user"):
            validated_data["author"] = request.user
        project = super().create(validated_data)
        # Ajoute le contributeur automatiquement
        Contributor.objects.create(user=project.author, project=project)
        return project

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["author"] = {
            "id": instance.author.id,
            "username": instance.author.username,
        }
        return rep


class ContributorSerializer(serializers.ModelSerializer):
    """
    Serializer for managing contributors in a project.

    **Features:**
    - The `user` field is automatically assigned to the authenticated user if not explicitly set.

    **Endpoints:**
    - `POST /api/contributors/` → Add a contributor.
    - `DELETE /api/contributors/{id}/` → Remove a contributor.

    **Example Usage (Python requests):**

        import requests
        headers = {"Authorization": "Bearer <token>"}
        data = {"project": 1}
        response = requests.post("http://127.0.0.1:8000/api/contributors/", json=data, headers=headers)
        print(response.json())

    """

    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Contributor
        fields = ["id", "user", "project"]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        # We update the representation to include more information about the user
        rep["user"] = {
            "id": instance.user.id,
            "username": instance.user.username,
        }
        return rep


class IssueSerializer(BaseAuthorSerializer):
    """
    Serializer for issue tracking within projects.

    Features:
    - Automatically assigns the current user as the issue's author.

    Endpoints:
    - POST /api/issues/ → Create an issue.
    - GET /api/issues/{id}/ → Retrieve issue details.
    """

    class Meta:
        model = Issue
        fields = [
            "id",
            "title",
            "description",
            "priority",
            "status",
            "author",
            "project",
            "created_time"
        ]
        read_only_fields = ["id", "created_time"]

    def to_representation(self, instance):
        """
        Returns a custom representation of the Issue instance, including author details.

        :param instance: The Issue instance.
        :type instance: Issue
        :return: A dictionary representation of the Issue, including author info.
        :rtype: dict
        """
        representation = super().to_representation(instance)
        representation["author"] = {
            "id": instance.author.id,
            "username": instance.author.username,
        }
        return representation


class CommentSerializer(BaseAuthorSerializer):
    """
    Serializer for comments on issues.

    Features:
    - Automatically assigns the current user as the comment's author.

    Endpoints:
    - POST /api/comments/ → Add a comment to an issue.
    - GET /api/comments/{id}/ → Retrieve comment details.

    Example usage (Python requests):

        import requests
        headers = {"Authorization": "Bearer <token>"}
        data = {"description": "I am working on this issue", "issue": 1}
        response = requests.post("http://127.0.0.1:8000/api/comments/", json=data, headers=headers)
        print(response.json())
    """

    class Meta:
        model = Comment
        fields = ["id", "description", "author", "issue", "created_time"]
        read_only_fields = ["id", "created_time"]

    def to_representation(self, instance):
        """
        Returns a custom representation of the Comment instance, including author details.

        :param instance: The Comment instance.
        :type instance: Comment
        :return: A dictionary representation of the Comment, including author info.
        :rtype: dict
        """
        representation = super().to_representation(instance)
        representation["author"] = {
            "id": instance.author.id,
            "username": instance.author.username,
        }
        return representation
