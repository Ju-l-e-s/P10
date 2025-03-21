import pytest
from rest_framework.test import APIClient
from support.factories import UserFactory, ProjectFactory, ContributorFactory

@pytest.mark.django_db
def test_contributor_access():
    """
    Ensure contributors can access project resources.
    """
    user = UserFactory()
    project = ProjectFactory()
    ContributorFactory(user=user, project=project)

    client = APIClient()
    client.force_authenticate(user=user)

    response = client.get(f"/api/projects/{project.id}/")
    assert response.status_code == 200
