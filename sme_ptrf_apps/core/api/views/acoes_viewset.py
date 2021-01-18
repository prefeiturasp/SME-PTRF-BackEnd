from django_filters import rest_framework as filters

from rest_framework import mixins

from rest_framework.permissions import IsAuthenticated

from rest_framework.viewsets import GenericViewSet

from ..serializers.acao_serializer import AcaoSerializer
from ...models import Acao


class AcoesViewSet(mixins.ListModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.CreateModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.DestroyModelMixin,
                   GenericViewSet):
    permission_classes = [IsAuthenticated]
    lookup_field = 'uuid'
    queryset = Acao.objects.all().order_by('nome')
    serializer_class = AcaoSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('nome',)
