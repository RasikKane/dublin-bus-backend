from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework import status
from user_auth.serializers import UserAuthSerializers

from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


class CustomAuthToken(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email,
            'first_name': user.first_name
        })


class UserAuthCreate(APIView):

    @staticmethod
    def is_user_unique(username):
        try:
            User.objects.get(username__exact=username)
            return False
        except:
            return True

    def post(self, request):
        serializer = UserAuthSerializers(data=request.data)
        if serializer.is_valid():
            user_unique = UserAuthCreate.is_user_unique(request.data['username'])
            print('user_unique: ', user_unique)
            if user_unique:
                user = User.objects.create_user(username=request.data['username'], email=request.data['username'],
                                                password=request.data['password'])
                user.first_name = request.data['first_name']
                user.last_name = request.data['last_name']
                user.save()
                return Response(serializer.validated_data, status=status.HTTP_201_CREATED)
            else:
                return Response('Username already exists', status=status.HTTP_409_CONFLICT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLogout(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        request.user.auth_token.delete()
        return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)


class CheckUserAuth(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            'user_id': user.pk,
            'email': user.email,
            'first_name': user.first_name
        })
