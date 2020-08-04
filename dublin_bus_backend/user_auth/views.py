from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from user_auth.serializers import UserAuthSerializers
import logging

# Create a logger for this file
logger = logging.getLogger(__file__)


class CustomAuthToken(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.serializer_class(data=request.data,
                                               context={'request': request})
            serializer.is_valid(raise_exception=True)
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
        except Exception as e:
            logger.exception('exception in user_auth view serializer', e)
            return Response({"Error: user_auth serializer"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            return Response({
                'token': token.key,
                'user_id': user.pk,
                'email': user.email,
                'first_name': user.first_name
            })
        except Exception as e:
            logger.exception('exception in user_auth view while returning JSON response', e)
            return Response({"Error: user_auth - valid JSON response not returned"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserAuthCreate(APIView):

    def post(self, request):
        try:
            serializer = UserAuthSerializers(data=request.data)
        except Exception as e:
            logger.exception('exception in user_auth view serializer creation', e)
            return Response({"Error: user_auth serializer"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            if serializer.is_valid():
                user = User.objects.create_user(username=request.data['username'], email=request.data['username'],
                                                password=request.data['password'])
                user.first_name = request.data['first_name']
                user.last_name = request.data['last_name']
                user.save()
                return Response(serializer.validated_data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.exception('exception in user_auth view UserAuthCreate class', e)
            return Response({"Error: user_auth - UserAuthCreate"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserLogout(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            request.user.auth_token.delete()
            return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.exception('exception in user_auth view UserLogout class', e)
            return Response({"Error: user_auth - UserLogout"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CheckUserAuth(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = request.user
            return Response({
                'user_id': user.pk,
                'email': user.email,
                'first_name': user.first_name
            })
        except Exception as e:
            logger.exception('exception in user_auth view CheckUserAuth class', e)
            return Response({"Error: user_auth - CheckUserAuth"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
