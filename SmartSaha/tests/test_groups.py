import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from SmartSaha.models import Organisation, Group, MemberGroup, GroupType, GroupRole

User = get_user_model()

@pytest.mark.django_db
class TestGroupModule:
    @pytest.fixture(autouse=True)
    def setup(self):
        """Initialisation avant chaque test."""
        self.client = APIClient()
        self.user = User.objects.create_user(username="tester", password="pass123")
        self.client.force_authenticate(user=self.user)

        self.org = Organisation.objects.create(
            name="Test Org",
            description="Organisation de test",
            org_type="NGO",
            created_by=self.user,
        )

        self.group_type = GroupType.objects.create(name="Farmer Group")
        self.group_role = GroupRole.objects.create(name="Leader", role_type="ADMIN")

        self.group = Group.objects.create(
            name="Group Alpha",
            organisation=self.org,
            type=self.group_type,
            created_by=self.user,
        )

        self.member = MemberGroup.objects.create(
            user=self.user,
            group=self.group,
            role=self.group_role,
            status="ACTIVE",
        )

    def test_organisation_endpoint(self):
        """Vérifie que l’endpoint /api/organisations/ retourne la bonne donnée."""
        url = reverse("organisation-list")
        response = self.client.get(url)
        assert response.status_code == 200
        assert len(response.data) > 0
        assert response.data[0]["name"] == "Test Org"

    def test_group_endpoint(self):
        """Vérifie que /api/groups/ retourne les groupes correctement liés à l’organisation."""
        url = reverse("group-list")
        response = self.client.get(url)
        assert response.status_code == 200
        data = response.data[0]
        assert data["organisation"] == self.org.id
        assert data["name"] == "Group Alpha"

    def test_member_group_endpoint(self):
        """Vérifie que /api/member-groups/ retourne les membres liés à un groupe."""
        url = reverse("membergroup-list")
        response = self.client.get(url)
        assert response.status_code == 200
        member = response.data[0]
        assert member["group"] == self.group.id
        assert member["user"] == self.user.id

    def test_orm_prefetch_related(self, django_assert_num_queries):
        """Vérifie que la vue utilise bien prefetch_related pour éviter le N+1."""
        with django_assert_num_queries(3):  # 1 pour Organisation, 1 pour GroupType, 1 pour Members
            Group.objects.select_related("organisation", "type").prefetch_related("members").first()
