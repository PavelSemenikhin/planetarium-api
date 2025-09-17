from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from user.serializers import RegisterSerializer, UserSerializer

User = get_user_model()


class UserSerializerTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="user@example.com",
            password="InitialPass123"
        )

    def test_read_only_id_field(self):
        serializer = UserSerializer(instance=self.user)
        self.assertEqual(serializer.data["id"], self.user.id)
        self.assertEqual(serializer.data["email"], self.user.email)
        self.assertNotIn("password", serializer.data)

    def test_update_email(self):
        serializer = UserSerializer(
            instance=self.user,
            data={"email": "new@example.com"},
            partial=True
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        updated_user = serializer.save()
        self.assertEqual(updated_user.email, "new@example.com")

    def test_update_password(self):
        serializer = UserSerializer(
            instance=self.user,
            data={"password": "NewStrongPass123"},
            partial=True
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        updated_user = serializer.save()
        self.assertTrue(updated_user.check_password("NewStrongPass123"))
