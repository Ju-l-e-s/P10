import factory
from django.contrib.auth import get_user_model
from support.models import Project, Contributor, Issue, Comment

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    """Factory for creating User instances."""
    class Meta:
        model = User

    username = factory.Faker("user_name")
    email = factory.Faker("email")
    password = factory.PostGenerationMethodCall("set_password", "testpass")


class ProjectFactory(factory.django.DjangoModelFactory):
    """Factory for creating Project instances."""
    class Meta:
        model = Project

    title = factory.Faker("sentence", nb_words=4)
    description = factory.Faker("text")
    type = factory.Iterator(["BACKEND", "FRONTEND", "IOS", "ANDROID"])
    author = factory.SubFactory(UserFactory)


class ContributorFactory(factory.django.DjangoModelFactory):
    """Factory for creating Contributor instances."""
    class Meta:
        model = Contributor

    user = factory.SubFactory(UserFactory)
    project = factory.SubFactory(ProjectFactory)


class IssueFactory(factory.django.DjangoModelFactory):
    """Factory for creating Issue instances."""
    class Meta:
        model = Issue

    title = factory.Faker("sentence", nb_words=6)
    description = factory.Faker("text")
    priority = factory.Iterator(["LOW", "MEDIUM", "HIGH"])
    status = factory.Iterator(["TODO", "IN_PROGRESS", "FINISHED"])
    project = factory.SubFactory(ProjectFactory)
    author = factory.SubFactory(UserFactory)


class CommentFactory(factory.django.DjangoModelFactory):
    """Factory for creating Comment instances."""
    class Meta:
        model = Comment

    description = factory.Faker("text")
    issue = factory.SubFactory(IssueFactory)
    author = factory.SubFactory(UserFactory)
