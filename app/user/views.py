from rest_framework import generics, authentication, permissions, status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from rest_framework.mixins import DestroyModelMixin
from rest_framework.response import Response
from user.serializers import (
    UserSerializer,
    AuthTokenSerializer,
    MoreTestsSerializer)


class CreateTokenView(ObtainAuthToken):  # creating token
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class AddNewManyTest(generics.CreateAPIView):
    serializer_class = MoreTestsSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]


class CreateUserView(generics.CreateAPIView):
    """create new user in system"""
    serializer_class = UserSerializer


class ManageUserView(generics.RetrieveUpdateDestroyAPIView, DestroyModelMixin):
    serializer_class = UserSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

# called when GET (retrieve), PUT/PATCH (update), or DELETE (destroy) NOT POST
# Instead of looking for a specific user by id, it automatically selects the logged-in user. # noqa
# This ensures users can only modify their own data, preventing them from modifying other users. # noqa

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"message": "Your account has been deleted successfully."},
            status=status.HTTP_200_OK
        )

    def get_object(self):
        return self.request.user
