from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from ..serializers import MotivoRejeicaoEncerramentoContaAssociacaoSerializer
from ...models import MotivoRejeicaoEncerramentoContaAssociacao
from ..utils.pagination import CustomPagination
class MotivoRejeicaoEncerramentoContaAssociacaoViewset(mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        mixins.CreateModelMixin,
                        mixins.UpdateModelMixin,
                        mixins.DestroyModelMixin,
                        GenericViewSet):
    permission_classes = [IsAuthenticated]
    lookup_field = 'uuid'
    queryset = MotivoRejeicaoEncerramentoContaAssociacao.objects.all()
    serializer_class = MotivoRejeicaoEncerramentoContaAssociacaoSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        qs = MotivoRejeicaoEncerramentoContaAssociacao.objects.all()

        nome = self.request.query_params.get('nome')

        if nome is not None:
            qs = qs.filter(nome__unaccent__icontains=nome)

        return qs
