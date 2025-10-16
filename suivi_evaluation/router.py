# suivi_evaluation/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import  reporting, evaluation, datalog, indicators

router = DefaultRouter()

# Indicators
router.register(r'indicators', indicators.IndicatorViewSet)
router.register(r'indicator-values', indicators.IndicatorValueViewSet)

# Reports
router.register(r'reporting', reporting.ReportViewSet)
router.register(r'report-data', reporting.ReportDataViewSet)
router.register(r'report-attachments', reporting.ReportAttachmentViewSet)

# Certifications
router.register(r'certification-types', evaluation.CertificationTypeViewSet)
router.register(r'evaluation', evaluation.CertificationViewSet)
router.register(r'certification-audits', evaluation.CertificationAuditViewSet)

# Data management
router.register(r'datalogs', datalog.DataLogViewSet)
router.register(r'custom-fields', datalog.CustomFieldViewSet)
router.register(r'custom-field-values', datalog.CustomFieldValueViewSet)

# # Geospatial
# router.register(r'parcels-evaluation', geospatial.ParcelEvaluationViewSet)
# router.register(r'geo-layers', geospatial.GeoLayerViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]
