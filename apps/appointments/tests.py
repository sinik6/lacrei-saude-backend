from datetime import datetime, timezone

from rest_framework import status
from rest_framework.test import APITestCase

from apps.appointments.models import Appointment
from apps.professionals.models import Professional
from apps.users.models import ApiKey


class AppointmentAPITestCase(APITestCase):
    def setUp(self):
        self.api_key = ApiKey.objects.create(name="Test Key")
        self.client.credentials(HTTP_X_API_KEY=self.api_key.key)
        self.professional = Professional.objects.create(
            nome_social="Dr. João Silva",
            profissao="Psicólogo",
            endereco="Rua das Flores, 123, São Paulo - SP",
            contato="(11) 99999-0001",
        )
        self.appointment = Appointment.objects.create(
            professional=self.professional,
            data=datetime(2026, 8, 15, 14, 0, tzinfo=timezone.utc),
        )
        self.list_url = "/api/v1/appointments/"
        self.detail_url = f"/api/v1/appointments/{self.appointment.pk}/"

    def test_list_appointments(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_create_appointment(self):
        data = {
            "professional": self.professional.pk,
            "data": "2026-09-10T10:00:00Z",
        }
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Appointment.objects.count(), 2)

    def test_create_appointment_missing_professional(self):
        data = {"data": "2026-09-10T10:00:00Z"}
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_appointment_missing_date(self):
        data = {"professional": self.professional.pk}
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_appointment_invalid_professional(self):
        data = {
            "professional": 99999,
            "data": "2026-09-10T10:00:00Z",
        }
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_appointment(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("professional_nome", response.data)
        self.assertEqual(response.data["professional_nome"], "Dr. João Silva")

    def test_retrieve_nonexistent_appointment(self):
        response = self.client.get("/api/v1/appointments/99999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_appointment(self):
        new_date = "2026-10-20T15:30:00Z"
        data = {"data": new_date}
        response = self.client.patch(self.detail_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.appointment.refresh_from_db()
        self.assertEqual(self.appointment.data.isoformat().replace("+00:00", "Z"), new_date)

    def test_full_update_appointment(self):
        new_professional = Professional.objects.create(
            nome_social="Dra. Maria Souza",
            profissao="Cardiologista",
            endereco="Av. Paulista, 1000, São Paulo - SP",
            contato="(11) 98888-0002",
        )
        data = {
            "professional": new_professional.pk,
            "data": "2026-12-01T09:00:00Z",
        }
        response = self.client.put(self.detail_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.appointment.refresh_from_db()
        self.assertEqual(self.appointment.professional, new_professional)

    def test_delete_appointment(self):
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Appointment.objects.count(), 0)

    def test_filter_by_professional(self):
        response = self.client.get(self.list_url, {"professional": self.professional.pk})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_cascade_delete(self):
        self.professional.delete()
        self.assertEqual(Appointment.objects.count(), 0)

    def test_unauthenticated_access_denied(self):
        client_no_auth = self.client_class()
        response = client_no_auth.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_appointment_with_invalid_date_format(self):
        data = {
            "professional": self.professional.pk,
            "data": "data-invalida",
        }
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_appointment_past_date(self):
        data = {
            "professional": self.professional.pk,
            "data": "2020-01-01T10:00:00Z",
        }
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_duplicate_appointment(self):
        data = {
            "professional": self.professional.pk,
            "data": "2026-09-10T10:00:00Z",
        }
        self.client.post(self.list_url, data, format="json")
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
