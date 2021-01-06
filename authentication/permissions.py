from rest_framework import permissions


class IsCurrentUser(permissions.BasePermission):
    message = {'errors': ['Permission denied']}

    def has_object_permission(self, request, view, obj):
        return obj.pk == request.user.pk
