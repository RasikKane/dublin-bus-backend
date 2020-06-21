from django.urls import path
from user_auth.views import CustomAuthToken, UserAuthCreate, UserLogout, CheckUserAuth
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    path('api-token-auth/', CustomAuthToken.as_view()),
    path('api-token-auth-check/', CheckUserAuth.as_view()),
    path('user/create', UserAuthCreate.as_view()),
    path('user/logout', UserLogout.as_view())
]

urlpatterns = format_suffix_patterns(urlpatterns)
