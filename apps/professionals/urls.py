from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.professionals.views import ProfessionalViewSet

router = DefaultRouter()
router.register(r"professionals", ProfessionalViewSet, basename="professional")

urlpatterns = [
    path("", include(router.urls)),
]
