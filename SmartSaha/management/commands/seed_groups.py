from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from SmartSaha.models import Organisation, GroupType, Group, GroupRole, MemberGroup
from django.utils import timezone

User = get_user_model()

class Command(BaseCommand):
    help = "Seeder pour les organisations, groupes et membres"

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Démarrage du seeding..."))

        # --- Utilisateur de test ---
        admin_user, _ = User.objects.get_or_create(
            username="admin",
            defaults={"email": "admin@test.com"}
        )

        # --- Organisation ---
        org, _ = Organisation.objects.get_or_create(
            name="Smart Saha Org",
            defaults={
                "description": "Organisation principale pour les tests",
                "org_type": "NGO",
                "created_by": admin_user,
            }
        )

        # --- Types de groupe ---
        farmer_type, _ = GroupType.objects.get_or_create(name="Farmer Group")
        coop_type, _ = GroupType.objects.get_or_create(name="Cooperative")

        # --- Rôles ---
        leader_role, _ = GroupRole.objects.get_or_create(name="Leader", role_type="ADMIN")
        member_role, _ = GroupRole.objects.get_or_create(name="Member", role_type="USER")

        # --- Groupes ---
        group1, _ = Group.objects.get_or_create(
            name="Green Farmers",
            organisation=org,
            type=farmer_type,
            defaults={
                "description": "Groupe des agriculteurs de la zone verte",
                "created_by": admin_user,
            },
        )
        group2, _ = Group.objects.get_or_create(
            name="Agri Coop",
            organisation=org,
            type=coop_type,
            defaults={
                "description": "Coopérative agricole test",
                "created_by": admin_user,
            },
        )

        # --- Membres ---
        MemberGroup.objects.get_or_create(
            user=admin_user,
            group=group1,
            role=leader_role,
            defaults={"status": "ACTIVE", "joined_at": timezone.now()},
        )

        MemberGroup.objects.get_or_create(
            user=admin_user,
            group=group2,
            role=member_role,
            defaults={"status": "ACTIVE", "joined_at": timezone.now()},
        )

        self.stdout.write(self.style.SUCCESS("Seeding terminé avec succès ✅"))
