from django.urls import path, include
from rest_framework.routers import DefaultRouter

from planetarium.views import (
    AstronomyShowViewSet,
    PlanetariumDomeViewSet,
    ShowSessionViewSet,
    ReservationViewSet,
    ShowThemeViewSet
)

app_name = "planetarium"

router = DefaultRouter()
router.register("astronomy-shows", AstronomyShowViewSet)
router.register("domes", PlanetariumDomeViewSet)
router.register("show-sessions", ShowSessionViewSet)
router.register("reservations", ReservationViewSet)
router.register("themes", ShowThemeViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
