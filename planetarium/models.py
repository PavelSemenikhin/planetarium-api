from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from config.settings import AUTH_USER_MODEL


class Presenter(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    class Meta:
        ordering = ["last_name", "first_name"]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class AstronomyShow(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    themes = models.ManyToManyField(
        "ShowTheme",
        related_name="shows"
    )
    presenter = models.ForeignKey(
        Presenter,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="shows"
    )

    def __str__(self):
        return self.title


class ShowTheme(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class PlanetariumDome(models.Model):
    name = models.CharField(max_length=100)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()

    def __str__(self):
        return f"{self.name}-{self.rows}-{self.seats_in_row}"

    @property
    def capacity(self) -> int:
        return self.rows * self.seats_in_row

    def clean(self):
        if self.rows < 1:
            raise ValidationError(
                {"rows": "Number of rows must be at least 1"}
            )
        if self.seats_in_row < 1:
            raise ValidationError(
                {"seats_in_row": "Number of seats must be at least 1"}
            )


class ShowSession(models.Model):
    astronomy_show = models.ForeignKey(
        AstronomyShow,
        on_delete=models.CASCADE,
        related_name="show_sessions"
    )
    planetarium_dome = models.ForeignKey(
        PlanetariumDome,
        on_delete=models.CASCADE
    )
    show_time = models.DateTimeField()

    class Meta:
        ordering = ["-show_time"]

    def __str__(self):
        return (f"{self.astronomy_show.title} "
                f"at {self.show_time.strftime('%Y-%m-%d %H:%M')}")


class Reservation(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reservations"
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username}-{self.created_at}"


class Ticket(models.Model):
    row = models.IntegerField()
    seat = models.IntegerField()
    show_session = models.ForeignKey(
        ShowSession,
        on_delete=models.CASCADE,
        related_name="tickets"
    )
    reservation = models.ForeignKey(
        Reservation,
        on_delete=models.CASCADE,
        related_name="tickets"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["show_session", "row", "seat"],
                name="unique_seat_per_session"
            )
        ]

    @staticmethod
    def validate_ticket(row, seat, cinema_hall, error_to_raise):
        for ticket_attr_value, ticket_attr_name, cinema_hall_attr_name in [
            (row, "row", "rows"),
            (seat, "seat", "seats_in_row"),
        ]:
            count_attrs = getattr(cinema_hall, cinema_hall_attr_name)
            if not (1 <= ticket_attr_value <= count_attrs):
                raise error_to_raise(
                    {
                        ticket_attr_name:
                            f"{ticket_attr_name} "
                            f"number must be in available range: "
                            f"(1, {cinema_hall_attr_name}): "
                            f"(1, {count_attrs})"
                    }
                )

    def clean(self):
        if self.show_session.show_time < timezone.now():
            raise ValidationError(
                {"show_session": "Cannot book a ticket for a past session."}
            )

        if Ticket.objects.filter(
                show_session=self.show_session,
                row=self.row,
                seat=self.seat
        ).exclude(pk=self.pk).exists():
            raise ValidationError(
                {"seat": "This seat is already taken for this session."}
            )

        Ticket.validate_ticket(
            self.row,
            self.seat,
            self.show_session.planetarium_dome,
            ValidationError,
        )

    def save(
        self,
        *args,
        force_insert=False,
        force_update=False,
        using=None,
        update_fields=None,
    ):
        self.full_clean()
        return super(Ticket, self).save(
            force_insert, force_update, using, update_fields
        )

    def __str__(self):
        return (f"{self.reservation.user.username}"
                f"-{self.row}"
                f"-{self.seat}"
                f"-{self.show_session}")
