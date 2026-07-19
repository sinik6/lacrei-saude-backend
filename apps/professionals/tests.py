from rest_framework import status
from rest_framework.test import APITestCase

from apps.professionals.models import Professional
from apps.users.models import ApiKey


class ProfessionalAPITestCase(APITestCase):
    def setUp(self):
        self.api_key = ApiKey.objects.create(name="Test Key")
        self.client.credentials(HTTP_X_API_KEY=self.api_key.key)
        self.professional = Professional.objects.create(
            nome_social="Dr. João Silva",
            profissao="Psicólogo",
            endereco="Rua das Flores, 123, São Paulo - SP",
            contato="(11) 99999-0001",
        )
        self.list_url = "/api/v1/professionals/"
        self.detail_url = f"/api/v1/professionals/{self.professional.pk}/"

    def test_list_professionals(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_create_professional(self):
        data = {
            "nome_social": "Dra. Maria Souza",
            "profissao": "Cardiologista",
            "endereco": "Av. Paulista, 1000, São Paulo - SP",
            "contato": "(11) 98888-0002",
        }
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Professional.objects.count(), 2)
        self.assertEqual(response.data["nome_social"], "Dra. Maria Souza")

    def test_create_professional_missing_field(self):
        data = {
            "nome_social": "Dr. Incompleto",
        }
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_professional_invalid_data(self):
        data = {
            "nome_social": "",
            "profissao": "",
            "endereco": "",
            "contato": "",
        }
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_professional(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["nome_social"], "Dr. João Silva")

    def test_retrieve_nonexistent_professional(self):
        response = self.client.get("/api/v1/professionals/99999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_professional(self):
        data = {"nome_social": "Dr. João Carlos Silva"}
        response = self.client.patch(self.detail_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.professional.refresh_from_db()
        self.assertEqual(self.professional.nome_social, "Dr. João Carlos Silva")

    def test_full_update_professional(self):
        data = {
            "nome_social": "Dr. João Carlos Silva",
            "profissao": "Psicólogo Clínico",
            "endereco": "Rua das Orquídeas, 456, São Paulo - SP",
            "contato": "(11) 97777-0003",
        }
        response = self.client.put(self.detail_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.professional.refresh_from_db()
        self.assertEqual(self.professional.endereco, "Rua das Orquídeas, 456, São Paulo - SP")

    def test_delete_professional(self):
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Professional.objects.count(), 0)

    def test_filter_by_profession(self):
        response = self.client.get(self.list_url, {"profissao": "Psicólogo"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_search_by_name(self):
        response = self.client.get(self.list_url, {"search": "João"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_unauthenticated_access_denied(self):
        client_no_auth = self.client_class()
        response = client_no_auth.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_sanitize_html_tags(self):
        data = {
            "nome_social": "<b>Dr. João</b>",
            "profissao": "Psicólogo",
            "endereco": "Rua X, 123",
            "contato": "<script>alert(1)</script>(11) 99999-0001",
        }
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["nome_social"], "Dr. João")
        self.assertEqual(response.data["contato"], "alert(1)(11) 99999-0001")
