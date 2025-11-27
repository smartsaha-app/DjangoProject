from django.contrib import admin
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework.routers import DefaultRouter
from django.shortcuts import redirect
from django.contrib.auth import views as auth_views

from SmartSaha.views.alerts import AlertViewSet
from SmartSaha.views.chatbot import GeminiAssistantViewSet, MistralAssistantViewSet
from suivi_evaluation.router import router as suivi_eval_router
from SmartSaha.router import router as groups_router

from SmartSaha.views import (
    ParcelViewSet, ParcelPointViewSet, UserViewSet, SignupView, LoginView,
    CropViewSet, StatusCropViewSet, VarietyViewSet, ParcelCropViewSet, TaskViewSet,
    TaskPriorityViewSet, TaskStatusViewSet, YieldRecordViewSet, SoilDataView,
    ClimateDataView, DataViewSet, ParcelFullDataViewSet, AgronomyAssistantAPIView,
    YieldForecastView, YieldAnalyticsView, DashboardViewSet, dashboard, tasks_view,
    assistant_agronome_page, assistant_agronome_api, WeatherDataViewSet, WeatherCollectionViewSet,
    AgriculturalAlertViewSet, AgriAssistantViewSet
)
from SmartSaha.views.users import ForgotPasswordView, ResetPasswordView, GoogleLoginView



# Redirection de la racine vers Swagger
def redirect_to_swagger(request):
    return redirect('schema-swagger-ui')

# Swagger schema
schema_view = get_schema_view(
    openapi.Info(
        title="Smart Saha API",
        default_version='v1',
        description="Documentation des endpoints de Smart Saha",
        contact=openapi.Contact(email="contact@smartsaha.mg"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

# Router API principal
router = DefaultRouter()
router.register(r'parcels', ParcelViewSet, basename='parcel')
router.register(r'parcel-points', ParcelPointViewSet)
router.register(r'users', UserViewSet)
router.register(r'crops', CropViewSet)
router.register(r'status-crops', StatusCropViewSet)
router.register(r'varieties', VarietyViewSet)
router.register(r'parcel-crops', ParcelCropViewSet, basename='parcelcrop')
router.register(r'tasks', TaskViewSet)
router.register(r'task-status', TaskStatusViewSet)
router.register(r'task-priority', TaskPriorityViewSet)
router.register(r'yield-records', YieldRecordViewSet)
router.register(r'external-data', DataViewSet, basename='external-data')
router.register(r'parcels-full', ParcelFullDataViewSet, basename='parcels-full')
router.register(r'dashboard', DashboardViewSet, basename='dashboard')


router.register(r'weather-data', WeatherDataViewSet, basename='weatherdata')

router.register(r'agricultural-alerts', AgriculturalAlertViewSet, basename='agriculturalalerts')

router.register(r'weather-collection', WeatherCollectionViewSet, basename='weathercollection')

router.register(r'alerts', AlertViewSet, basename='alert')

router.register(r'assistant', AgriAssistantViewSet, basename='assistant')

router.register(r'gemini-assistant', GeminiAssistantViewSet, basename='gemini-assistant')

router.register(r'mistral-assistant', MistralAssistantViewSet, basename='mistral-assistant')

urlpatterns = [
    path('', redirect_to_swagger, name='home'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # Auth
    path('api/signup/', SignupView.as_view(), name='signup'),
    path('api/login/', LoginView.as_view(), name='login'),
    path("api/google-login/", GoogleLoginView.as_view(), name="google-login"),
    path("api/forgot-password/", ForgotPasswordView.as_view(), name="forgot-password"),
    path("api/reset-password/<uidb64>/<token>/", ResetPasswordView.as_view(), name="reset-password"),

    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    # DRF router principal
    path('api/', include(router.urls)),

    # Router suivi-évaluation
    path('api/suivi-evaluation/', include(suivi_eval_router.urls)),
    path('api/groups/', include(groups_router.urls)),

    # Admin
    path('admin/', admin.site.urls),

    # Pages HTML
    path("dashboard/", dashboard, name="dashboard"),
    path('tasks/', tasks_view, name='tasks'),
    # path('parcels/<uuid:parcel_uuid>/view/', parcel_full_data_page, name='parcel-full-data-page'),
    path("assistant-agronome/", assistant_agronome_page, name="assistant_agronome_page"),

    # API spécifiques / non CRUD
    path("api/assistant-agronome/", assistant_agronome_api, name="assistant-agronome_api"),
    path("api/soil-data/", SoilDataView.as_view(), name="soil-data"),
    path("api/climate-data/", ClimateDataView.as_view(), name="climate-data"),
    path('forecast/<int:parcel_crop_id>/', YieldForecastView.as_view(), name='yield_forecast'),
    path("analytics/yields/", YieldAnalyticsView.as_view(), name="yield-analytics"),


]
