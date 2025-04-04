from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers
from django.utils.translation import gettext as _
from core.models import MoreTests


class MoreTestsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MoreTests
        fields = ['his_id', 'name']

    def create(self, validated_data):
        return MoreTests.objects.add(**validated_data)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['email', 'password', 'name']
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}

# all for password hashing , can be used without create and update but it will store password as plain text # noqa

    def create(self, validated_data):
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user


class AuthTokenSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(style={'input_type': 'password'}, trim_whitespace=False,) # noqa

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password,
        )
        if not user:
            msg = _('unable to authinicate this user')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs
