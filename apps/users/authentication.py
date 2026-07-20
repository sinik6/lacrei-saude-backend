from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from apps.users.models import ApiKey


class ApiKeyAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get("X-API-Key")

        if not auth_header:
            return None

        try:
            api_key = ApiKey.objects.get(key=auth_header, is_active=True)
        except ApiKey.DoesNotExist as err:
            raise AuthenticationFailed("API Key inválida ou inativa.") from err

        return (None, api_key)

    def authenticate_header(self, request):
        return 'X-API-Key realm="api"'
