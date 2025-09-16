from .parcels import ParcelCreateView,ParcelViewSet, ParcelPointViewSet, ParcelFullDataViewSet, parcel_full_data_page
from  .users import UserViewSet, LoginView, SignupView,ForgotPasswordView,ResetPasswordView
from .cultures import CropViewSet,VarietyViewSet,StatusCropViewSet,ParcelCropViewSet
from .tasks import TaskViewSet, TaskStatusViewSet , TaskPriorityViewSet, tasks_view
from .yelds import YieldRecordViewSet,YieldAnalyticsView
from .externalData import SoilDataView,ClimateDataView, DataViewSet
from .deepseek import AgronomyAssistantAPIView, assistant_agronome_api, assistant_agronome_page
from .forecast import YieldForecastView
from .dashboard import dashboard
from .dashboard import DashboardViewSet