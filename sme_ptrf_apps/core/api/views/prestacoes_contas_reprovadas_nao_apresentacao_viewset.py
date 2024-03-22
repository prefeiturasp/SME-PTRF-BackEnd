from rest_framework import mixins, status
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated
from waffle.mixins import WaffleFlagMixin
from sme_ptrf_apps.users.permissoes import PermissaoApiUe

from ..serializers.prestacao_conta_reprovada_nao_apresentacao_serializer import \
    PrestacaoContaReprovadaNaoApresentacaoSerializer, PrestacaoContaReprovadaNaoApresentacaoCreateSerializer

from ...models.prestacao_conta_reprovada_nao_apresentacao import PrestacaoContaReprovadaNaoApresentacao


class PrestacaoContaReprovadaNaoApresentacaoViewSet(
    WaffleFlagMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet
):
    waffle_flag = "pc-reprovada-nao-apresentacao"
    permission_classes = [IsAuthenticated & PermissaoApiUe]
    lookup_field = 'uuid'
    queryset = PrestacaoContaReprovadaNaoApresentacao.objects.all().order_by(
        'associacao__unidade__tipo_unidade',
        'associacao__unidade__nome'
    )
    serializer_class = PrestacaoContaReprovadaNaoApresentacaoSerializer

    def get_serializer_class(self):
        if self.action in ['retrieve', 'list']:
            return PrestacaoContaReprovadaNaoApresentacaoSerializer
        else:
            return PrestacaoContaReprovadaNaoApresentacaoCreateSerializer
