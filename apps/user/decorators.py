from django.http import HttpResponse, JsonResponse

from apps.user.authentication import TokenAuthentication
from apps.user.exceptions import AuthenticationFailed


def logged_in(function):

    def _inner(self, request, *args, **kwargs):
        try:
            authentication = TokenAuthentication.authenticate(request=request)
        except AuthenticationFailed as error:
            return JsonResponse({'error': 103, "message": str(error)})

        if isinstance(authentication, HttpResponse):
            return authentication

        request.player = authentication[0]

        if not request.player:
            return JsonResponse({'error': 104, "message": "Permission denied as not valid was found."})
        return function(self, request, *args, **kwargs)

    return _inner
