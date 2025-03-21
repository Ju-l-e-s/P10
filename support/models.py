from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.

    **Additional fields:**
    - `age` (optional): Age of the user.
    - `can_be_contacted`: Whether the user agrees to be contacted.
    - `can_data_be_shared`: Whether the user allows data sharing.

    :ivar age: The user's age (optional, must be positive).
    :vartype age: int
    :ivar can_be_contacted: Indicates if the user agrees to be contacted.
    :vartype can_be_contacted: bool
    :ivar can_data_be_shared: Indicates if the user's data can be shared.
    :vartype can_data_be_shared: bool
    """

    age = models.PositiveIntegerField(null=True, blank=True)
    can_be_contacted = models.BooleanField(default=False)
    can_data_be_shared = models.BooleanField(default=False)

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"


class Project(models.Model):
    """
    Project model representing a software development project.

    **Project Types:**
    - BACKEND
    - FRONTEND
    - IOS
    - ANDROID

    **Relationships:**
    - `author`: The user who created the project.
    - `contributors`: Users who contribute to the project.

    :ivar title: The project title.
    :vartype title: str
    :ivar description: A detailed description of the project.
    :vartype description: str
    :ivar type: The project type (backend, frontend, iOS, Android).
    :vartype type: str
    :ivar author: The creator of the project.
    :vartype author: User
    :ivar created_time: Timestamp when the project was created.
    :vartype created_time: datetime
    """

    BACKEND = "BACKEND"
    FRONTEND = "FRONTEND"
    IOS = "IOS"
    ANDROID = "ANDROID"

    PROJECT_TYPES = [
        (BACKEND, "Back-end"),
        (FRONTEND, "Front-end"),
        (IOS, "iOS"),
        (ANDROID, "Android"),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    type = models.CharField(max_length=10, choices=PROJECT_TYPES)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="projects")
    created_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Contributor(models.Model):
    """
    Contributor model representing a user contributing to a project.

    **Relationships:**
    - `user`: The user contributing.
    - `project`: The project they contribute to.

    **Constraints:**
    - A user can only contribute to a project **once** (unique_together constraint).

    :ivar user: The contributor user.
    :vartype user: User
    :ivar project: The project they contribute to.
    :vartype project: Project
    :ivar created_time: Timestamp when the contributor was added.
    :vartype created_time: datetime
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="contributors")
    created_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'project')


class Issue(models.Model):
    """
    Issue model representing a bug, task, or feature request within a project.

    **Priority Levels:**
    - LOW
    - MEDIUM
    - HIGH

    **Tags:**
    - BUG
    - FEATURE
    - TASK

    **Status:**
    - TODO
    - IN_PROGRESS
    - FINISHED

    **Relationships:**
    - `project`: The project the issue belongs to.
    - `author`: The user who created the issue.
    - `assignee`: The user assigned to resolve the issue.

    :ivar title: The issue title.
    :vartype title: str
    :ivar description: A detailed description of the issue.
    :vartype description: str
    :ivar priority: The priority level (low, medium, high).
    :vartype priority: str
    :ivar tag: The category of the issue (bug, feature, task).
    :vartype tag: str
    :ivar status: The current status (to do, in progress, finished).
    :vartype status: str
    :ivar project: The project related to this issue.
    :vartype project: Project
    :ivar author: The user who created the issue.
    :vartype author: User
    :ivar assignee: The user assigned to work on the issue.
    :vartype assignee: User
    :ivar created_time: Timestamp when the issue was created.
    :vartype created_time: datetime
    """

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    PRIORITIES = [
        (LOW, "Low"),
        (MEDIUM, "Medium"),
        (HIGH, "High"),
    ]

    BUG = "BUG"
    FEATURE = "FEATURE"
    TASK = "TASK"
    TAGS = [
        (BUG, "Bug"),
        (FEATURE, "Feature"),
        (TASK, "Task"),
    ]

    TODO = "TODO"
    IN_PROGRESS = "IN PROGRESS"
    FINISHED = "FINISHED"
    STATUS = [
        (TODO, "To Do"),
        (IN_PROGRESS, "In Progress"),
        (FINISHED, "Finished"),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITIES)
    tag = models.CharField(max_length=10, choices=TAGS)
    status = models.CharField(max_length=15, choices=STATUS, default=TODO)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="issues")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="issues")
    assignee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_issues")
    created_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Comment(models.Model):
    """
    Comment model for issues.

    **Relationships:**
    - `issue`: The issue the comment is linked to.
    - `author`: The user who posted the comment.

    :ivar issue: The issue being commented on.
    :vartype issue: Issue
    :ivar author: The user who wrote the comment.
    :vartype author: User
    :ivar description: The comment text.
    :vartype description: str
    :ivar created_time: Timestamp when the comment was created.
    :vartype created_time: datetime
    """

    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comments")
    description = models.TextField()
    created_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author.username} on {self.issue.title}"
