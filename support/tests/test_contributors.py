# support/tests/test_contributors.py
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from support.models import Project, Contributor

User = get_user_model()


@pytest.mark.django_db
class ContributorTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.other_user = User.objects.create_user(username="otheruser", password="testpass")
        self.client.force_authenticate(user=self.user)

        self.project = Project.objects.create(
            author=self.user,
            title="Test Project",
            description="A test project",
            type="BACKEND"
        )
        Contributor.objects.create(user=self.user, project=self.project)

        self.contributor_data = {
            "user": self.other_user.id,
            "project": self.project.id
        }

    def test_add_contributor(self):
        response = self.client.post("/api/contributors/", self.contributor_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_contributors(self):
        # Add the second contributor
        Contributor.objects.create(user=self.other_user, project=self.project)

        response = self.client.get("/api/contributors/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)  # Maintenant 2 contributeurs (user + other_user)
        self.assertEqual(len(response.data["results"]), 2)

    def test_remove_contributor(self):
        contributor = Contributor.objects.create(user=self.other_user, project=self.project)

        # check if the URL matches the API schema
        response = self.client.delete(f"/api/contributors/{contributor.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
