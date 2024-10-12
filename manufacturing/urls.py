from django.urls import path, include
from rest_framework.routers import DefaultRouter
from manufacturing.views import AircraftViewSet, TeamViewSet, PartViewSet, PersonnelViewSet, AircraftPartViewSet, \
    RegisterView, UserView

# Create a router for the API, which will automatically generate URL patterns for the viewsets
router = DefaultRouter()
router.register(r'aircrafts', AircraftViewSet)  # Route for aircraft-related operations
router.register(r'teams', TeamViewSet)          # Route for team-related operations
router.register(r'parts', PartViewSet)          # Route for part-related operations
router.register(r'personnel', PersonnelViewSet) # Route for personnel-related operations
router.register(r'aircraftparts', AircraftPartViewSet)  # Route for aircraft part associations

urlpatterns = [
    path('', include(router.urls)),  # Include all routes defined in the router
    path('register/', RegisterView.as_view(), name='register'),  # Route for user registration
    path('user/me/', UserView.as_view(), name='user-me'),  # Route for retrieving the current user's information
]
