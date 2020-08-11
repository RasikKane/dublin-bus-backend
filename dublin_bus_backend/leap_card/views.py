from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from pyleapcard import LeapSession
import logging

# Create a logger handle for this file
logger = logging.getLogger(__file__)


# card_info(<session_in>) returns card overview information retrieved from active session of leapcard.ie
def card_info(session_in):
    overview = vars(session_in.get_card_overview())
    return overview


# obtain and return card overview for requested user credentials
class LeapCardGetUserInfo(APIView):

    def post(self, request):

        username = str(request.data.get('username'))
        password = str(request.data.get('password'))
        try:
            # start and acquire leap card session
            session = LeapSession()
            session.try_login(username, password)
            # obtain json response from leapcard.ie
            content = card_info(session)
        except Exception as e:
            logger.error('exception in leap_card view LeapCardGetUserInfo object')
            logger.exception(e)
            return Response({"Something went wrong! Enter valid credentials for active student leap card account"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Create JSON response
        payload = [content]
        # print(payload)
        try:
            return JsonResponse(payload, safe=False)
        except Exception as e:
            logger.error('exception in leap_card view while returning JSON response')
            logger.exception(e)
            return Response({"Something went wrong! Please try again later"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
