from django.contrib import admin

# Register your models here.
from django.contrib import admin
from SmartSaha.models import Group, MemberGroup

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ("name", "organisation", "type", "status")

@admin.register(MemberGroup)
class MemberGroupAdmin(admin.ModelAdmin):
    list_display = ("user", "group", "role", "status")
