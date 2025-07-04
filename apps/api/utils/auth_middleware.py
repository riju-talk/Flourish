import jwt
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth import get_user_model
from rest_framework import exceptions
from rest_framework.authentication import get_authorization_header
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

User = get_user_model()

class SupabaseJWTAuthenticationMiddleware(MiddlewareMixin):
    """
    Middleware to handle Supabase JWT authentication.
    Extracts the JWT from cookies or Authorization header, verifies it,
    and sets request.user to the corresponding user.
    """
    
    def process_request(self, request):
        # Skip middleware for OPTIONS requests and public endpoints
        if request.method == 'OPTIONS' or request.path in ['/api/health/']:
            return None
            
        # Try to get the token from the cookie first
        token = request.COOKIES.get('access_token')
        
        # If no token in cookie, try the Authorization header
        if not token:
            auth_header = get_authorization_header(request).split()
            if auth_header and len(auth_header) == 2 and auth_header[0].lower() == b'bearer':
                token = auth_header[1].decode('utf-8')
            
        if not token:
            return None
            
        try:
            # Verify and decode the JWT
            try:
                # First try to validate as a Django JWT
                UntypedToken(token)
                # If we get here, it's a Django JWT
                user = self._get_user_from_jwt(token)
            except (InvalidToken, TokenError):
                # If not a Django JWT, try as Supabase JWT
                user = self._get_user_from_supabase_jwt(token)
            
            # Set the user on the request
            request.user = user
            
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Token has expired')
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed('Invalid token')
        except Exception as e:
            raise exceptions.AuthenticationFailed(str(e))
            
        return None
    
    def _get_user_from_jwt(self, token):
        """Get user from Django JWT token"""
        from rest_framework_simplejwt.authentication import JWTAuthentication
        jwt_auth = JWTAuthentication()
        validated_token = jwt_auth.get_validated_token(token)
        return jwt_auth.get_user(validated_token)
    
    def _get_user_from_supabase_jwt(self, token):
        """Get or create user from Supabase JWT token"""
        try:
            payload = jwt.decode(
                token,
                settings.SUPABASE_JWT_SECRET,
                algorithms=['HS256'],
                audience='authenticated',
                options={"verify_aud": True}
            )
            
            # Get or create the user
            user, _ = User.objects.get_or_create(
                email=payload.get('email'),
                defaults={
                    'username': payload.get('email'),
                    'is_active': True
                }
            )
            
            return user
            
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Token has expired')
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed('Invalid token')
        except Exception as e:
            raise exceptions.AuthenticationFailed(str(e))
