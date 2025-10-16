import uuid
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

# TODO: creation d'un model organisation role encore inconnu
class Organisation(models.Model):
    class OrganisationType(models.TextChoices):
        GOVERNMENT = "GOVERNMENT", "Gouvernementale"
        NGO = "NGO", "ONG"
        PRIVATE = "PRIVATE", "Privée"
        COOP = "COOP", "Coopérative"
        OTHER = "OTHER", "Autre"

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150, unique=True)
    description = models.TextField(blank=True, null=True)
    org_type = models.CharField(
        max_length=50,
        choices=OrganisationType.choices,
        default=OrganisationType.OTHER
    )
    address = models.CharField(max_length=255, blank=True, null=True)
    contact_email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="organisations_created")
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="organisations_updated")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name



# TODO: creation d'un model typeGroup pour enum (coop,groups,... )
class GroupType(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

# TODO: creation d'un model groups pour declarer un groups
class Group(models.Model):
    class GroupStatus(models.TextChoices):
        ACTIVE = "ACTIVE", "Actif"
        INACTIVE = "INACTIVE", "Inactif"
        SUSPENDED = "SUSPENDED", "Suspendu"

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150, unique=True)
    description = models.TextField(blank=True, null=True)
    type = models.ForeignKey(GroupType, on_delete=models.SET_NULL, null=True, related_name="groups")
    organisation = models.ForeignKey(Organisation, on_delete=models.SET_NULL, null=True, related_name="groups")
    status = models.CharField(max_length=20, choices=GroupStatus.choices, default=GroupStatus.ACTIVE)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="groups_created")
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="groups_updated")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["organisation"]),
            models.Index(fields=["type"]),
        ]

# TODO: creation d'un model role pour gerer les roles des utilisateurs dans le(s) group(s)
class GroupRole(models.Model):
    class RoleType(models.TextChoices):
        LEADER = "LEADER", "Chef de groupe"
        SECRETARY = "SECRETARY", "Secrétaire"
        MEMBER = "MEMBER", "Membre"
        AUDITOR = "AUDITOR", "Auditeur interne"
        OTHER = "OTHER", "Autre"

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    role_type = models.CharField(
        max_length=50,
        choices=RoleType.choices,
        default=RoleType.MEMBER
    )

    def __str__(self):
        return self.name


# TODO: creation d'un model MemberGroup pour rassembler 2 ou plusieurs users dans un meme groups
class MemberGroup(models.Model):
    class MembershipStatus(models.TextChoices):
        ACTIVE = "ACTIVE", "Actif"
        INACTIVE = "INACTIVE", "Inactif"
        PENDING = "PENDING", "En attente"

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="group_memberships")
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="members")
    role = models.ForeignKey(GroupRole, on_delete=models.SET_NULL, null=True, related_name="members_with_role")
    status = models.CharField(max_length=20, choices=MembershipStatus.choices, default=MembershipStatus.ACTIVE)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["group"]),
            models.Index(fields=["role"]),
        ]
        unique_together = ("user", "group")

    def __str__(self):
        return f"{self.user.username} - {self.group.name}"
