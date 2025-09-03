"""
URL configuration for SmaartSahaProject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from SmartSaha.views import ParcelViewSet, ParcelPointViewSet, UserViewSet, SignupView, LoginView, CropViewSet, \
    StatusCropViewSet, VarietyViewSet, ParcelCropViewSet, TaskViewSet, TaskPriorityViewSet, TaskStatusViewSet
from SmartSaha.views.users import ForgotPasswordView, ResetPasswordView

router = DefaultRouter()
router.register(r'parcels', ParcelViewSet)
router.register(r'parcel-points', ParcelPointViewSet)
router.register(r'users', UserViewSet)
router.register(r'crops', CropViewSet)
router.register(r'status-crops', StatusCropViewSet)
router.register(r'varieties', VarietyViewSet)
router.register(r'parcel-crops', ParcelCropViewSet)
router.register(r'tasks', TaskViewSet)
router.register(r'task-priorities', TaskPriorityViewSet)
router.register(r'task-statuses', TaskStatusViewSet)
urlpatterns = [
    path('api/signup/', SignupView.as_view(), name='signup'),
    path('api/login/', LoginView.as_view(), name='login'),
    path("api/forgot-password/", ForgotPasswordView.as_view(), name="forgot-password"),
    path("api/reset-password/<uidb64>/<token>/", ResetPasswordView.as_view(), name="reset-password"),
    path('api/', include(router.urls)),
    path('admin/', admin.site.urls),
]
