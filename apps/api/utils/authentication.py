from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed
from rest_framework import status
from django.conf import settings

class CookieJWTAuthentication(JWTAuthentication):
    """
    An authentication plugin that authenticates requests through a JSON web
    token provided in a request cookie (and through the standard header).
    """
    def authenticate(self, request):
        # Try to get the token from the cookie first
        raw_token = request.COOKIES.get(settings.JWT_AUTH.get('JWT_AUTH_COOKIE', 'access_token'))
        
        # If no token in cookie, try the header
        if not raw_token:
            return super().authenticate(request)
            
        # Validate the token
        validated_token = self.get_validated_token(raw_token)
        return self.get_user(validated_token), validated_token

class RefreshTokenAuthentication(CookieJWTAuthentication):
    """
    An authentication plugin that authenticates refresh token requests through a
    JSON web token provided in a request cookie.
    """
    def authenticate(self, request):
        # Only allow POST requests for refresh
        if request.method != 'POST':
            return None
            
        raw_token = request.COOKIES.get(settings.JWT_AUTH.get('JWT_AUTH_REFRESH_COOKIE', 'refresh_token'))
        
        if not raw_token:
            return None
            
        try:
            validated_token = self.get_validated_token(raw_token)
            return self.get_user(validated_token), validated_token
        except Exception as e:
            raise AuthenticationFailed(
                {'detail': 'Invalid or expired refresh token'},
                code='authentication_failed'
            )

def get_tokens_for_user(user):
    """
    Generate access and refresh tokens for the given user
    """
    from rest_framework_simplejwt.tokens import RefreshToken
    
    refresh = RefreshToken.for_user(user)
    
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }
