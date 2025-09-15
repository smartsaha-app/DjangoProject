from .parcels import ParcelCreateView,ParcelViewSet, ParcelPointViewSet, ParcelFullDataViewSet
from  .users import UserViewSet, LoginView, SignupView,ForgotPasswordView,ResetPasswordView
from .cultures import CropViewSet,VarietyViewSet,StatusCropViewSet,ParcelCropViewSet
from .tasks import TaskViewSet, TaskStatusViewSet , TaskPriorityViewSet
from .yelds import YieldRecordViewSet,YieldAnalyticsView
from .externalData import SoilDataView,ClimateDataView, DataViewSet
from .deepseek import AgronomyAssistantAPIView
from .forecast import YieldForecastView
from .dashboard import DashboardViewSet