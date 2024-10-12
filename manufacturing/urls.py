from django.urls import path, include
from rest_framework.routers import DefaultRouter
from manufacturing.views import AircraftViewSet, TeamViewSet, PartViewSet, PersonnelViewSet, AircraftPartViewSet, \
    RegisterView, UserView

router = DefaultRouter()
router.register(r'aircrafts', AircraftViewSet)
router.register(r'teams', TeamViewSet)
router.register(r'parts', PartViewSet)
router.register(r'personnel', PersonnelViewSet)
router.register(r'aircraftparts', AircraftPartViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('register/', RegisterView.as_view(), name='register'),
    path('user/me/', UserView.as_view(), name='user-me'),
]
