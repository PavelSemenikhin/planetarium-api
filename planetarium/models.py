from django.db import models

from config.settings import AUTH_USER_MODEL


class AstronomyShow(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    themes = models.ManyToManyField(
        "ShowTheme",
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

    def __str__(self):
        return (f"{self.reservation.user.username}"
                f"-{self.row}"
                f"-{self.seat}"
                f"-{self.show_session}")
