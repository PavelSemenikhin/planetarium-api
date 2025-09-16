from django.contrib.auth import get_user_model
from rest_framework import serializers


User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer used only for registering a new user."""
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={"input_type": "password"}
    )

    class Meta:
        model = User
        fields = ("email", "password")

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserSerializer(serializers.ModelSerializer):
    """Serializer for retrieving and updating user profile."""
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        required=False,
        style={"input_type": "password"}
    )

    class Meta:
        model = User
        fields = ("id", "email", "password")
        read_only_fields = ("id",)

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user
