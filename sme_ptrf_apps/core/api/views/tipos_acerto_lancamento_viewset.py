from rest_framework import mixins

from rest_framework.permissions import IsAuthenticated

from rest_framework.viewsets import GenericViewSet

from ..serializers.tipo_acerto_lancamento_serializer import TipoAcertoLancamentoSerializer
from ...models import TipoAcertoLancamento
from sme_ptrf_apps.users.permissoes import PermissaoApiUe


class TiposAcertoLancamentoViewSet(mixins.ListModelMixin,
                                   mixins.RetrieveModelMixin,
                                   GenericViewSet):
    permission_classes = [IsAuthenticated & PermissaoApiUe]
    lookup_field = 'uuid'
    queryset = TipoAcertoLancamento.objects.all()
    serializer_class = TipoAcertoLancamentoSerializer
