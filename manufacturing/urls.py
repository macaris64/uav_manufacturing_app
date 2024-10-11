from django.urls import path, include
from rest_framework.routers import DefaultRouter
from manufacturing.views import AircraftViewSet, TeamViewSet, PartViewSet, PersonnelViewSet, AircraftPartViewSet

router = DefaultRouter()
router.register(r'aircrafts', AircraftViewSet)
router.register(r'teams', TeamViewSet)
router.register(r'parts', PartViewSet)
router.register(r'personnel', PersonnelViewSet)
router.register(r'aircraftparts', AircraftPartViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
