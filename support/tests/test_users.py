import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
def test_user_creation():
    """Test creation of a user"""
    user = User.objects.create_user(username="testuser", password="testpassword")
    assert user.username == "testuser"
