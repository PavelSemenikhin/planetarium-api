
from rest_framework import viewsets, mixins

from planetarium.models import AstronomyShow, PlanetariumDome, ShowSession
from planetarium.serializers import (
    AstronomyShowSerializer,
    AstronomyShowListSerializer,
    AstronomyShowDetailSerializer,
    PlanetariumDomeSerializer,
    ShowSessionSerializer,
    ShowSessionListSerializer,
    ShowSessionDetailSerializer
)


class AstronomyShowViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = (AstronomyShow.objects
                .select_related("presenter")
                .prefetch_related("themes"))
    serializer_class = AstronomyShowSerializer
    permission_classes = ...

    def get_queryset(self):
        return (AstronomyShow.objects
                .select_related("presenter")
                .prefetch_related("themes"))

    def get_serializer_class(self):
        if self.action == "list":
            return AstronomyShowListSerializer
        if self.action == "retrieve":
            return AstronomyShowDetailSerializer
        return AstronomyShowSerializer


class PlanetariumShowViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    queryset = PlanetariumDome.objects.all()
    serializer_class = PlanetariumDomeSerializer
    permission_classes = ...


class ShowSessionViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    queryset = (ShowSession.objects
                .select_related(
                    "astronomy_show__presenter", "planetarium_dome")
                .prefetch_related("tickets")
                )
    serializer_class = ShowSessionSerializer
    permission_classes = ...

    def get_queryset(self):
        return self.queryset

    def get_serializer_class(self):
        if self.action == "list":
            return ShowSessionListSerializer
        if self.action == "retrieve":
            return ShowSessionDetailSerializer
        return ShowSessionSerializer
