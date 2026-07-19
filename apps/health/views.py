from django.db import connection
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(["GET"])
@permission_classes([AllowAny])
def health_check(request):
    db_ok = False
    try:
        connection.ensure_connection()
        db_ok = True
    except Exception:
        db_ok = False

    status_code = 200 if db_ok else 503

    return Response(
        {
            "status": "ok" if db_ok else "degraded",
            "versao": "1.0.0",
            "servico": "lacrei-saude-api",
            "database": "connected" if db_ok else "unavailable",
        },
        status=status_code,
    )
