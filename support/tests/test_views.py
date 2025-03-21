import pytest
from rest_framework.test import APIClient
from support.factories import UserFactory, ProjectFactory
from rest_framework import status
from django.core.cache import cache

@pytest.mark.django_db
def test_project_list_view():
    """
    Test project list API endpoint with pagination.
    """
    user = UserFactory()
    cache.clear()
    ProjectFactory.create_batch(3, author=user) # create 3 projects
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.get("/api/projects/")
    assert response.status_code == 200

    # pagination => the "count" field corresponds to the total number of projects
    assert response.data["count"] == 3
    # "results" contains the current page
    assert len(response.data["results"]) == 3
