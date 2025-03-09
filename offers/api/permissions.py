from rest_framework.permissions import BasePermission

class IsOwnerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        """
        Returns True if the user is the owner of the object, or if the user is an admin.
        """
        return request.user == obj.user or request.user.is_staff