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

    def get_queryset(self):
        qs = Acao.objects.all()

        nome = self.request.query_params.get('nome')
        if nome is not None:
            qs = qs.filter(nome__unaccent__icontains=nome)

        return qs.order_by('nome')
