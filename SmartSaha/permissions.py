from rest_framework import permissions
import logging


logger = logging.getLogger(__name__)


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Seuls les admins peuvent modifier ; les autres peuvent juste lire.
    """
    def has_permission(self, request, view):
        logger.info(f"User {request.user} tried to {request.method}")
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff


class IsGroupLeader(permissions.BasePermission):
    """
    Seuls les membres avec un rôle 'Leader' dans le groupe peuvent modifier.
    """
    def has_object_permission(self, request, view, obj):
        logger.info(f"User {request.user} tried to access {obj}")
        if request.method in permissions.SAFE_METHODS:
            return True
        member = obj.members.filter(user=request.user).first()
        return member and member.role.name.lower() in ["admin", "leader"]


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    L’utilisateur doit être le créateur (created_by) ou un admin global.
    """
    def has_object_permission(self, request, view, obj):
        logger.info(f"User {request.user} tried to access {obj}")
        return (
            obj.created_by == request.user
            or (request.user and request.user.is_staff)
        )

class CanAssignRole(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Superuser → tout accès
        if request.user.is_superuser:
            return True
        from SmartSaha.models import MemberGroup
        # Vérifie que l’utilisateur est manager du groupe concerné
        return MemberGroup.objects.filter(
            user=request.user,
            group=obj.group,
            role__name="LEADER",
            status="ACTIVE"
        ).exists()
