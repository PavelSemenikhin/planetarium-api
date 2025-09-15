from rest_framework import serializers

from planetarium.models import (
    AstronomyShow,
    PlanetariumDome,
    Presenter,
    ShowTheme,
    ShowSession,
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

    class Meta:
        model = AstronomyShow
        fields = ("id", "title", "description", "themes", "presenter")


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

    class Meta:
        model = AstronomyShow
        fields = ("id", "title", "description", "themes", "presenter")


class PresenterFromShowMixin:
    """Mixin for retrieving the presenter's full name
    from the related AstronomyShow."""
    presenter = serializers.SerializerMethodField()

    def get_presenter(self, obj):
        return obj.astronomy_show.presenter.full_name \
            if obj.astronomy_show.presenter else None


class ShowSessionSerializer(
    PresenterFromShowMixin,
    serializers.ModelSerializer
):
    """Base serializer used for creating ShowSession instances."""
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

    class Meta:
        model = ShowSession
        fields = (
            "id",
            "astronomy_show",
            "planetarium_dome",
            "presenter",
            "taken_places",
            "taken_seats",
        )

    def get_taken_places(self, obj):
        return obj.tickets.count()

    def get_taken_seats(self, obj):
        return [
            {"row": ticket.row, "seat": ticket.seat}
            for ticket in obj.tickets.all()
        ]
