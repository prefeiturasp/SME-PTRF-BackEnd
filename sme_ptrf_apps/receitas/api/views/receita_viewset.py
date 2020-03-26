from rest_framework import mixins
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import GenericViewSet

from sme_ptrf_apps.receitas.models import Receita
from ..serializers import ReceitaCreateSerializer


class ReceitaViewSet(mixins.CreateModelMixin,
                     GenericViewSet):
    lookup_field = 'uuid'
    permission_classes = [AllowAny]
    queryset = Receita.objects.all()
    serializer_class = ReceitaCreateSerializer
