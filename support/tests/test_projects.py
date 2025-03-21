import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from support.models import Project

User = get_user_model()


@pytest.mark.django_db
class ProjectTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.client.force_authenticate(user=self.user)
        self.project_data = {
            "title": "Test Project",
            "description": "A test project",
            "type": "BACKEND"
        }

    def test_create_project(self):
        response = self.client.post("/api/projects/", self.project_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_projects(self):
        Project.objects.create(author=self.user, **self.project_data)
        response = self.client.get("/api/projects/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Vérif pagination => "count" et "results"
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(len(response.data["results"]), 1)

    def test_update_project(self):
        project = Project.objects.create(author=self.user, **self.project_data)
        response = self.client.patch(f"/api/projects/{project.id}/", {"title": "Updated"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Updated")

    def test_delete_project(self):
        project = Project.objects.create(author=self.user, **self.project_data)
        response = self.client.delete(f"/api/projects/{project.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
