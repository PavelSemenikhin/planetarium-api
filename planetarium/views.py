
from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated

from planetarium.models import (
    AstronomyShow,
    PlanetariumDome,
    ShowSession,
    Reservation,
    ShowTheme
)
from planetarium.permissions import IsAdminOrReadOnly
from planetarium.serializers import (
    AstronomyShowSerializer,
    AstronomyShowListSerializer,
    AstronomyShowDetailSerializer,
    PlanetariumDomeSerializer,
    ShowSessionSerializer,
    ShowSessionListSerializer,
    ShowSessionDetailSerializer,
    ReservationSerializer,
    ReservationListSerializer,
    ShowThemeSerializer
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
    permission_classes = [IsAdminOrReadOnly]

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


class PlanetariumDomeViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    queryset = PlanetariumDome.objects.all()
    serializer_class = PlanetariumDomeSerializer
    permission_classes = [IsAdminOrReadOnly]


class ShowSessionViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = (
        ShowSession.objects.select_related(
            "astronomy_show",
            "astronomy_show__presenter",
            "planetarium_dome",
        )
    )
    serializer_class = ShowSessionSerializer
    permission_classes = [IsAdminOrReadOnly]

    @staticmethod
    def _params_to_ints(qs):
        """Converts a list of string IDs to a list of integers"""
        return [int(str_id) for str_id in qs.split(",")]

    def get_queryset(self):
        """Retrieve the sessions with optional filters."""
        queryset = super().get_queryset()

        theme = self.request.query_params.get("theme")
        show_time = self.request.query_params.get("show_time")
        title = self.request.query_params.get("title")

        if theme:
            queryset = queryset.filter(
                astronomy_show__themes__name__icontains=theme
            )

        if show_time:
            queryset = queryset.filter(
                show_time__date=show_time
            )

        if title:
            queryset = queryset.filter(
                astronomy_show__title__icontains=title
            )

        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == "list":
            return ShowSessionListSerializer
        if self.action == "retrieve":
            return ShowSessionDetailSerializer
        return ShowSessionSerializer


class ReservationViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Reservation.objects.prefetch_related(
        "tickets__show_session__astronomy_show",
        "tickets__show_session__planetarium_dome"
    )
    serializer_class = ReservationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Reservation.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return ReservationListSerializer
        return ReservationSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ShowThemeViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    queryset = ShowTheme.objects.all()
    serializer_class = ShowThemeSerializer
    permission_classes = [IsAdminOrReadOnly]
