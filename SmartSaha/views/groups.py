from rest_framework import viewsets, filters, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Prefetch
from django_filters.rest_framework import DjangoFilterBackend
from SmartSaha.permissions import IsGroupManager, IsAdminOrReadOnly, IsOwnerOrAdmin, CanAssignRole
from SmartSaha.models import Organisation, GroupType, Group, GroupRole, MemberGroup
from SmartSaha.serializers import (
    OrganisationSerializer,
    GroupTypeSerializer,
    GroupSerializer,
    GroupRoleSerializer,
    MemberGroupSerializer,
)

# --- BASE VIEWSET RÉUTILISABLE ---
class BaseModelViewSet(viewsets.ModelViewSet):
    """
    Classe de base commune pour tous les ViewSets.
    Fournit les comportements communs : permissions, filtres, recherches, etc.
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    ordering_fields = ["created_at", "updated_at"]
    search_fields = ["name"]
    pagination_class = None

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


# --- ORGANISATIONS ---
class OrganisationViewSet(BaseModelViewSet):
    queryset = Organisation.objects.all().order_by("-created_at")
    serializer_class = OrganisationSerializer
    filterset_fields = ["org_type"]
    search_fields = ["name", "description"]
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]  # Seuls les admins peuvent créer/supprimer


# --- TYPES DE GROUPES ---
class GroupTypeViewSet(BaseModelViewSet):
    queryset = GroupType.objects.all().order_by("name")
    serializer_class = GroupTypeSerializer
    search_fields = ["name"]
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]  # Lecture libre, écriture admin


# --- GROUPES ---
class GroupViewSet(BaseModelViewSet):
    queryset = (
        Group.objects.select_related("organisation", "type", "created_by", "updated_by")
        .prefetch_related(
            Prefetch("members", queryset=MemberGroup.objects.filter(status="ACTIVE"))
        )
        .order_by("-created_at")
    )
    serializer_class = GroupSerializer
    filterset_fields = ["status", "organisation", "type"]
    search_fields = ["name", "description"]
    permission_classes = [IsAuthenticated, IsGroupManager | IsOwnerOrAdmin]
    # => Managers et propriétaires peuvent modifier, admin a tous les droits

    def perform_create(self, serializer):
        group = serializer.save(created_by=self.request.user)

        # Récupération du rôle "Manager" (ou création s’il n’existe pas)
        leader_role, _ = GroupRole.objects.get_or_create(
            role_type=GroupRole.RoleType.LEADER,
            defaults={"name": "Chef de groupe"}
        )

        # Ajoute automatiquement le créateur comme membre du groupe avec rôle LEADER
        MemberGroup.objects.get_or_create(
            user=self.request.user,
            group=group,
            role=leader_role,
            defaults={"status": "ACTIVE"}
        )
        return group

# --- ROLES DE GROUPES ---
class GroupRoleViewSet(BaseModelViewSet):
    queryset = GroupRole.objects.all().order_by("name")
    serializer_class = GroupRoleSerializer
    search_fields = ["name", "role_type"]
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]  # Lecture pour tous, écriture admin


# --- MEMBRES DE GROUPES ---
class MemberGroupViewSet(BaseModelViewSet):
    queryset = (
        MemberGroup.objects
        .select_related("user", "group", "role")
        .order_by("-joined_at")
    )
    serializer_class = MemberGroupSerializer
    filterset_fields = ["status", "group", "role"]
    search_fields = ["user__username", "group__name"]
    permission_classes = [IsAuthenticated, IsGroupManager | IsOwnerOrAdmin, CanAssignRole]
    # => Un membre ne peut modifier que ses propres infos ou si c’est un manager/admin
