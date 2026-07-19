from rest_framework import status
from rest_framework.test import APITestCase

from apps.users.models import ApiKey


class ApiKeyAuthTestCase(APITestCase):
    def setUp(self):
        self.api_key = ApiKey.objects.create(name="Test Key")
        self.list_url = "/api/v1/professionals/"

    def test_valid_api_key(self):
        self.client.credentials(HTTP_X_API_KEY=self.api_key.key)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_api_key(self):
        self.client.credentials(HTTP_X_API_KEY="invalid-key-12345")
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_missing_api_key(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_inactive_api_key_denied(self):
        inactive_key = ApiKey.objects.create(name="Inactive", is_active=False)
        self.client.credentials(HTTP_X_API_KEY=inactive_key.key)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_multiple_endpoints_protected(self):
        self.client.credentials(HTTP_X_API_KEY=self.api_key.key)
        urls = [
            "/api/v1/professionals/",
            "/api/v1/appointments/",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"Falha em {url}")
