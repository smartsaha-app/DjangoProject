from django.urls import path, include
from rest_framework.routers import DefaultRouter
from SmartSaha.views import (
    OrganisationViewSet,
    GroupTypeViewSet,
    GroupViewSet,
    GroupRoleViewSet,
    MemberGroupViewSet,
)

# --- ROUTER PRINCIPAL ---
router = DefaultRouter()
router.register(r'organisations', OrganisationViewSet, basename='organisation')
router.register(r'group-types', GroupTypeViewSet, basename='group-type')
router.register(r'groups', GroupViewSet, basename='group')
router.register(r'group-roles', GroupRoleViewSet, basename='group-role')
router.register(r'member-groups', MemberGroupViewSet, basename='member-group')

urlpatterns = [
    path('', include(router.urls)),
]
