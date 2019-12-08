import jwt
from django.conf import settings

from django.http import JsonResponse

from apps.user.models import Player
from .exceptions import AuthenticationFailed


class TokenAuthentication:

    @staticmethod
    def authenticate(request):
        auth = TokenAuthentication.get_authorization_header(request).split()
        if not auth or auth[0].lower() != 'bearer':
            return None
        if len(auth) == 1:
            msg = 'Invalid token header. No credentials provided.'
            raise AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = 'Invalid token header'
            raise AuthenticationFailed(msg)

        try:
            token = auth[1]
            if token == "null":
                msg = 'Null token not allowed'
                raise AuthenticationFailed(msg)
        except UnicodeError:
            msg = 'Invalid token header. Token string should not contain invalid characters.'
            raise AuthenticationFailed(msg)

        return TokenAuthentication.authenticate_credentials(token)

    @staticmethod
    def authenticate_credentials(token):
        try:
            payload = jwt.decode(token, settings.SECRET_KEY)
            player_id = payload['id']
            player = Player.objects.get(
                id=player_id,
                is_active=True
            )

        except jwt.ExpiredSignature or jwt.DecodeError or jwt.InvalidTokenError:
            msg = 'Invalid token'
            raise AuthenticationFailed(msg)

        return player, token

    @staticmethod
    def get_authorization_header(request):
        return request.headers.get('authorization')
