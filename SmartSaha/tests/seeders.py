from SmartSaha.models import Organisation, GroupType, Group, GroupRole, MemberGroup

def seed_organisation():
    org = Organisation.objects.create(name="Org Test", org_type="AGRI")
    return org

def seed_group_type():
    return GroupType.objects.create(name="Type Test")

def seed_group(org, group_type):
    return Group.objects.create(name="Group Test", organisation=org, type=group_type)

def seed_group_role():
    return GroupRole.objects.create(name="Role Test", role_type="ADMIN")

def seed_member(user, group, role):
    return MemberGroup.objects.create(user=user, group=group, role=role, status="ACTIVE")
