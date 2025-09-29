from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from planetarium.models import (
    AstronomyShow,
    PlanetariumDome,
    Presenter,
    ShowTheme,
    ShowSession, Reservation, Ticket,
)


class PresenterSerializer(serializers.ModelSerializer):
    """Serializer for listing and retrieving Presenter instances."""
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = Presenter
        fields = ("id", "first_name", "last_name", "full_name")


class ShowThemeSerializer(serializers.ModelSerializer):
    """Serializer for creating, listing,
     and retrieving ShowTheme instances."""

    class Meta:
        model = ShowTheme
        fields = ("id", "name")


class PlanetariumDomeSerializer(serializers.ModelSerializer):
    """Serializer for creating, listing,
    and retrieving PlanetariumDome instances."""
    capacity = serializers.ReadOnlyField()

    class Meta:
        model = PlanetariumDome
        fields = ("id", "name", "rows", "seats_in_row", "capacity")


class AstronomyShowSerializer(serializers.ModelSerializer):
    """Base serializer used for creating AstronomyShow instances."""
    themes = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=ShowTheme.objects.all()
    )

    class Meta:
        model = AstronomyShow
        fields = (
            "id",
            "title",
            "description",
            "themes",
            "presenter",
            "poster"
        )


class AstronomyShowListSerializer(AstronomyShowSerializer):
    """Serializer for listing AstronomyShow instances."""
    themes = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="name"
    )
    presenter = serializers.SlugRelatedField(
        read_only=True,
        slug_field="full_name"
    )

    class Meta:
        model = AstronomyShow
        fields = ("id", "title", "description", "themes", "presenter")


class AstronomyShowDetailSerializer(AstronomyShowSerializer):
    """Serializer for retrieving detailed information
    about an AstronomyShow."""
    themes = ShowThemeSerializer(many=True, read_only=True)
    presenter = PresenterSerializer(read_only=True)
    poster = serializers.ImageField(read_only=True)

    class Meta:
        model = AstronomyShow
        fields = (
            "id",
            "title",
            "description",
            "themes",
            "presenter",
            "poster"
        )


class PresenterFromShowMixin:
    """Mixin for retrieving the presenter's full name
    from the related AstronomyShow."""
    presenter = serializers.CharField(
        source="astronomy_show.presenter.full_name", read_only=True)

    def get_presenter(self, obj):
        return obj.astronomy_show.presenter.full_name \
            if obj.astronomy_show.presenter else None


class ShowSessionSerializer(
    PresenterFromShowMixin,
    serializers.ModelSerializer
):
    """Base serializer used for creating ShowSession instances."""
    presenter = serializers.CharField(
        source="astronomy_show.presenter.full_name",
        read_only=True)

    astronomy_show = serializers.SlugRelatedField(
        read_only=True,
        slug_field="title"
    )

    class Meta:
        model = ShowSession
        fields = ("id", "astronomy_show", "presenter", "show_time")


class ShowSessionListSerializer(ShowSessionSerializer):
    """Serializer for listing ShowSession instances."""
    pass


class ShowSessionDetailSerializer(ShowSessionSerializer):
    """Serializer for retrieving detailed Show Session info
    including seats taken."""
    taken_places = serializers.SerializerMethodField()
    astronomy_show = AstronomyShowListSerializer(read_only=True)
    planetarium_dome = PlanetariumDomeSerializer(read_only=True)
    taken_seats = serializers.SerializerMethodField()
    is_full = serializers.BooleanField(read_only=True)

    class Meta:
        model = ShowSession
        fields = (
            "id",
            "astronomy_show",
            "planetarium_dome",
            "presenter",
            "taken_places",
            "taken_seats",
            "is_full",
        )

    def get_taken_places(self, obj):
        return obj.tickets.count()

    def get_taken_seats(self, obj):
        return list(obj.tickets.values("row", "seat"))


class TicketSerializer(serializers.ModelSerializer):
    """Serializer for creating and validating Ticket instances."""

    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "show_session")
        read_only_fields = ("id",)

    def validate(self, attrs):
        """Validate row and seat for the given planetarium dome."""
        Ticket.validate_ticket(
            attrs["row"],
            attrs["seat"],
            attrs["show_session"].planetarium_dome,
            ValidationError
        )
        return attrs


class ReservationSerializer(serializers.ModelSerializer):
    """Serializer for creating Reservation instances with nested Tickets."""
    user = serializers.SlugRelatedField(read_only=True, slug_field="username")
    tickets = TicketSerializer(many=True,)

    class Meta:
        model = Reservation
        fields = ("id", "user", "created_at", "tickets")

    def create(self, validated_data):
        """Create reservation and associated tickets
        within atomic transaction."""
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            reservation = Reservation.objects.create(**validated_data)
            for ticket_data in tickets_data:
                Ticket.objects.create(reservation=reservation, **ticket_data)
            return reservation


class ReservationListSerializer(ReservationSerializer):
    """Serializer for listing Reservation instances with nested Tickets."""
    tickets = TicketSerializer(many=True, read_only=True)
