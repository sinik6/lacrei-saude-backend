from rest_framework.permissions import BasePermission


class HasValidApiKey(BasePermission):
    def has_permission(self, request, view):
        return bool(request.auth)
