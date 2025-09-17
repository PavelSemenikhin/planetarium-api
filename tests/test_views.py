from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


SHOW_URL = reverse("planetarium:astronomyshow-list")
SHOW_SESSION_URL = reverse("planetarium:showsession-list")
DOME_URL = reverse("planetarium:planetariumdome-list")

class UnauthenticatedPlanetariumApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_list_astronomy_shows(self):
        response = self.client.get(SHOW_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_astronomy_show_unauthorized(self):
        payload = {
            "title": "Test Show",
            "description": "Interesting stuff",
            "presenter": 1,
            "themes": [],
        }
        response = self.client.post(SHOW_URL, data=payload)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_show_sessions(self):
        response = self.client.get(SHOW_SESSION_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_show_session_unauthorized(self):
        response = self.client.post(SHOW_SESSION_URL, data={})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_dome(self):
        response = self.client.get(DOME_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_dome_unauthorized(self):
        response = self.client.post(DOME_URL, data={})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedUserPlanetariumApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="pasha@gmail.com",
            password="pasha1122"
        )
        self.client.force_authenticate(self.user)

    def test_user_cannot_create_show(self):
        response = self.client.post(SHOW_URL, data={})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_can_list_shows(self):
        response = self.client.get(SHOW_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
