import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from support.models import Project, Contributor, Issue

User = get_user_model()


@pytest.mark.django_db
class IssueTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.client.force_authenticate(user=self.user)

        self.project = Project.objects.create(
            author=self.user,
            title="Test Project",
            description="A test project",
            type="BACKEND"
        )
        Contributor.objects.create(user=self.user, project=self.project)

        self.issue_data = {
            "title": "Test Issue",
            "description": "Issue description",
            "priority": "HIGH",
            "status": "TODO"
        }

    def test_create_issue(self):
        """
        Un contributeur peut créer une issue => permission IsContributor + IsResourceAuthorOrReadOnly
        """
        response = self.client.post("/api/issues/", {"project": self.project.id, **self.issue_data}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_issues(self):
        """
        Lister les issues => pagination => vérifie count et results.
        """
        Issue.objects.create(author=self.user, project=self.project, **self.issue_data)
        response = self.client.get("/api/issues/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(len(response.data["results"]), 1)

    def test_update_issue(self):
        """
        Seul l'auteur d'une issue peut la modifier => IsResourceAuthorOrReadOnly
        """
        issue = Issue.objects.create(author=self.user, project=self.project, **self.issue_data)
        response = self.client.patch(f"/api/issues/{issue.id}/", {"title": "Updated Issue"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Updated Issue")

    def test_update_issue_non_author(self):

        issue = Issue.objects.create(author=self.user, project=self.project, **self.issue_data)
        other_user = User.objects.create_user(username="otheruser", password="otherpass")
        self.client.force_authenticate(user=other_user)
        response = self.client.patch(f"/api/issues/{issue.id}/", {"title": "Unauthorized Update"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_issue(self):
        issue = Issue.objects.create(author=self.user, project=self.project, **self.issue_data)
        response = self.client.delete(f"/api/issues/{issue.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
