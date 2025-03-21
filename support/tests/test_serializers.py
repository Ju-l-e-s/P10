import pytest
from rest_framework.test import APIRequestFactory
from rest_framework.request import Request
from support.serializers import ProjectSerializer

@pytest.mark.django_db
def test_invalid_project_type():
    factory = APIRequestFactory()
    django_request = factory.post("/fake-url/")
    django_request.user = None

    drf_request = Request(django_request)
    data = {
        "title": "Test Project",
        "description": "A sample project",
        "type": "INVALID_TYPE"
    }
    serializer = ProjectSerializer(data=data, context={"request": drf_request})
    assert not serializer.is_valid()
    assert "type" in serializer.errors
