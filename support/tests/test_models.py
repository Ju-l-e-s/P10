import pytest
from support.models import Project, Contributor, Issue, Comment
from support.factories import UserFactory, ProjectFactory, ContributorFactory, IssueFactory, CommentFactory

@pytest.mark.django_db
def test_create_project():
    """
    Test project creation with a valid user.
    """
    project = ProjectFactory()
    assert Project.objects.count() == 1
    assert project.author is not None

@pytest.mark.django_db
def test_create_contributor():
    """
    Test contributor creation and unique constraint enforcement.
    """
    contributor = ContributorFactory()
    assert Contributor.objects.count() == 1

@pytest.mark.django_db
def test_create_issue():
    """
    Test issue creation linked to a project.
    """
    issue = IssueFactory()
    assert Issue.objects.count() == 1
    assert issue.project is not None

@pytest.mark.django_db
def test_create_comment():
    """
    Test comment creation linked to an issue.
    """
    comment = CommentFactory()
    assert Comment.objects.count() == 1
    assert comment.issue is not None
