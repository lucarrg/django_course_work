from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views

app_name = 'coworking_api'

router = DefaultRouter()
router.register(r'coworkings', api_views.CoworkingViewSet)
router.register(r'workplaces', api_views.WorkplaceViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
