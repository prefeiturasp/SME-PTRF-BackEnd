from django.contrib.auth import get_user_model
from rest_framework import viewsets, mixins
from rest_framework.permissions import AllowAny

from sme_ptrf_apps.users.api.serializers import EsqueciMinhaSenhaSerializer

User = get_user_model()


class EsqueciMinhaSenhaViewSet(viewsets.ModelViewSet):
    lookup_field = 'username'
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = EsqueciMinhaSenhaSerializer
