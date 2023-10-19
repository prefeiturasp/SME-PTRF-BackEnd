from django.contrib.auth.middleware import get_user
from django.utils.functional import SimpleLazyObject
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken

class JWTAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.user = SimpleLazyObject(lambda: self.get_jwt_user(request))
        return self.get_response(request)

    def get_jwt_user(self, request):
        user = get_user(request)
        if user.is_authenticated:
            return user

        try:
            authenticated_tuple = JWTAuthentication().authenticate(request)
            if authenticated_tuple:
                user, jwt = authenticated_tuple
        except InvalidToken:
            return AnonymousUser()

        return user if user and user.is_authenticated else AnonymousUser()
