from rest_framework import serializers
from django.contrib.auth import get_user_model
from SmartSaha.models import Organisation, GroupType, Group, GroupRole, MemberGroup

User = get_user_model()

class OrganisationSerializer(serializers.ModelSerializer):
    created_by = serializers.SlugRelatedField(
        slug_field="username", read_only=True
    )
    updated_by = serializers.SlugRelatedField(
        slug_field="username", read_only=True
    )

    class Meta:
        model = Organisation
        fields = [
            "uuid", "name", "description", "org_type", "address",
            "contact_email", "phone", "created_by", "updated_by",
            "created_at", "updated_at"
        ]
        read_only_fields = ["uuid", "created_at", "updated_at"]

class GroupTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupType
        fields = ["uuid", "name", "description"]
        read_only_fields = ["uuid"]

class GroupSerializer(serializers.ModelSerializer):
    type = GroupTypeSerializer(read_only=True)
    type_id = serializers.PrimaryKeyRelatedField(
        source="type",
        queryset=GroupType.objects.all(),
        write_only=True
    )
    organisation = OrganisationSerializer(read_only=True)
    organisation_id = serializers.PrimaryKeyRelatedField(
        source="organisation",
        queryset=Organisation.objects.all(),
        write_only=True
    )
    created_by = serializers.SlugRelatedField(slug_field="username", read_only=True)
    updated_by = serializers.SlugRelatedField(slug_field="username", read_only=True)

    class Meta:
        model = Group
        fields = [
            "uuid", "name", "description", "status",
            "type", "type_id",
            "organisation", "organisation_id",
            "created_by", "updated_by",
            "created_at", "updated_at"
        ]
        read_only_fields = ["uuid", "created_at", "updated_at"]

class GroupRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupRole
        fields = ["uuid", "name", "description", "role_type"]
        read_only_fields = ["uuid"]

class MemberGroupSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(slug_field="username", read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        source="user",
        queryset=User.objects.all(),
        write_only=True
    )
    group = GroupSerializer(read_only=True)
    group_id = serializers.PrimaryKeyRelatedField(
        source="group",
        queryset=Group.objects.all(),
        write_only=True
    )
    role = GroupRoleSerializer(read_only=True)
    role_id = serializers.PrimaryKeyRelatedField(
        source="role",
        queryset=GroupRole.objects.all(),
        write_only=True
    )

    class Meta:
        model = MemberGroup
        fields = [
            "uuid", "user", "user_id", "group", "group_id",
            "role", "role_id", "status", "joined_at"
        ]
        read_only_fields = ["uuid", "joined_at"]
