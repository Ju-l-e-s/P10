import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from support.models import Project, Issue, Comment, Contributor

User = get_user_model()


@pytest.mark.django_db
class CommentTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.client.force_authenticate(user=self.user)

        self.project = Project.objects.create(
            title="Test Project",
            description="A test project",
            type="BACKEND",
            author=self.user
        )
        Contributor.objects.create(user=self.user, project=self.project)

        self.issue = Issue.objects.create(
            title="Test Issue",
            description="A test issue",
            priority="HIGH",
            status="TODO",
            author=self.user,
            project=self.project
        )

        self.comment_data = {
            "description": "Test Comment",
            "issue": self.issue.id
        }

    def test_create_comment(self):
        """
        L'utilisateur (contributeur) peut créer un commentaire => permission IsContributor + IsResourceAuthorOrReadOnly
        """
        response = self.client.post("/api/comments/", self.comment_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_comments(self):
        """
        Lister tous les commentaires => usage de la pagination => on vérifie count et results.
        """
        Comment.objects.create(author=self.user, issue=self.issue, description="Test Comment")
        response = self.client.get("/api/comments/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)  # total d'objets
        self.assertEqual(len(response.data["results"]), 1)  # objets sur cette page

    def test_update_comment(self):
        """
        Seul l'auteur du commentaire peut le modifier => IsResourceAuthorOrReadOnly.
        """
        comment = Comment.objects.create(author=self.user, issue=self.issue, description="Old Comment")
        response = self.client.patch(f"/api/comments/{comment.id}/", {"description": "Updated Comment"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["description"], "Updated Comment")

    def test_delete_comment(self):
        """
        Only the author of the comment can delete it.
        """
        comment = Comment.objects.create(author=self.user, issue=self.issue, description="Test Comment")
        response = self.client.delete(f"/api/comments/{comment.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
