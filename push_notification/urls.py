from django.urls import path, include
from rest_framework import routers

from . import api
from . import views

from .api import FCMDeviceAuthorizedViewSet, FCMDeviceViewSet

router = routers.DefaultRouter()
router.register(r'app', api.AppViewSet)
router.register(r'fcm/devices', FCMDeviceViewSet)

urlpatterns = (
    # urls for Django Rest Framework API
    path('api/v1/', include(router.urls)),
        # DRF browsable API which lists all available endpoints
    # url('api/v1/fcm/', include(router.urls)),
)

urlpatterns += (
    # urls for App
    path('push_notification/app/', views.AppListView.as_view(), name='push_notification_app_list'),
    path('push_notification/app/create/', views.AppCreateView.as_view(), name='push_notification_app_create'),
    path('push_notification/app/detail/<int:pk>/', views.AppDetailView.as_view(), name='push_notification_app_detail'),
    path('push_notification/app/update/<int:pk>/', views.AppUpdateView.as_view(), name='push_notification_app_update'),
)


