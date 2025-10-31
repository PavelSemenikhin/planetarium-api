from django.utils import timezone
from django.core.exceptions import ValidationError
from django.test import TestCase
from planetarium.models import (
    Presenter, ShowTheme, AstronomyShow, PlanetariumDome,
    ShowSession, Reservation, Ticket
)
from user.models import User


class PlanetariumModelsTests(TestCase):
    def setUp(self):
        self.presenter = Presenter.objects.create(first_name="Carl", last_name="Sagan")
        self.theme = ShowTheme.objects.create(name="Cosmos")
        self.dome = PlanetariumDome.objects.create(name="Main Dome", rows=5, seats_in_row=10)
        self.user = User.objects.create_user(
            email="pavlentiy@gmail.com",
            password="pasha22335"
        )
        self.show = AstronomyShow.objects.create(title="Black Holes", description="A deep dive", presenter=self.presenter)
        self.show.themes.add(self.theme)
        self.session = ShowSession.objects.create(
            astronomy_show=self.show,
            planetarium_dome=self.dome,
            show_time=timezone.now() + timezone.timedelta(days=1)
        )
        self.reservation = Reservation.objects.create(user=self.user)
        self.ticket = Ticket.objects.create(
            row=1,
            seat=1,
            show_session=self.session,
            reservation=self.reservation
        )

    def test_presenter_str_and_full_name(self):
        self.assertEqual(str(self.presenter), "Carl Sagan")
        self.assertEqual(self.presenter.full_name, "Carl Sagan")

    def test_show_theme_str(self):
        self.assertEqual(str(self.theme), "Cosmos")

    def test_astronomy_show_str(self):
        self.assertEqual(str(self.show), "Black Holes")

    def test_planetarium_dome_str_and_capacity(self):
        self.assertEqual(str(self.dome), "Main Dome-5-10")
        self.assertEqual(self.dome.capacity, 50)

    def test_planetarium_dome_clean_invalid(self):
        with self.assertRaises(ValidationError):
            PlanetariumDome(name="Tiny", rows=0, seats_in_row=10).clean()
        with self.assertRaises(ValidationError):
            PlanetariumDome(name="Tiny", rows=3, seats_in_row=0).clean()

    def test_show_session_str_and_props(self):
        self.assertIn("Black Holes", str(self.session))
        self.assertEqual(self.session.available_seats, 49)
        self.assertFalse(self.session.is_full)
