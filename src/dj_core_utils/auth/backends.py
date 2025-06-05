from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth.models import AnonymousUser
from django.conf import settings


class CustomJWTAuthentication(JWTAuthentication):
    """
    Custom backend that:
    - Validates JWT tokens
    - Supports service-to-service authentication
    """

    def authenticate(self, request):
        # 1. Intenta autenticación JWT estándar
        try:
            user_token = super().authenticate(request)
            if user_token:
                return user_token
        except Exception:
            pass

        # 2. Fallback a autenticación servicio-servicio
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Service '):
            api_key = auth_header.split(' ')[1]
            if api_key == getattr(settings, 'SERVICE_API_KEY', ''):
                return (AnonymousUser(), None)

        # 3. No autenticado
        return None
