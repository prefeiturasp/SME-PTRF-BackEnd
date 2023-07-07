from django_filters import rest_framework as filters
from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.viewsets import GenericViewSet
from rest_framework.filters import SearchFilter

from ..serializers import GrupoSerializer
from ...models import Grupo

class GruposViewSet(mixins.ListModelMixin, GenericViewSet):
    # TODO: Voltar a usar IsAuthenticated
    # permission_classes = [IsAuthenticated]
    permission_classes = [AllowAny]

    lookup_field = 'id'
    queryset = Grupo.objects.all().order_by('name')
    serializer_class = GrupoSerializer
    filter_backends = (filters.DjangoFilterBackend, SearchFilter,)
    search_fields = ['name', 'descricao', ]
    filter_fields = ('visoes__id', 'visoes__nome')
