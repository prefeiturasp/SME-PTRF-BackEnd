import logging

from datetime import datetime

from waffle.mixins import WaffleFlagMixin

from rest_framework.decorators import action
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

# from sme_ptrf_apps.core.services.paa_service import gerar_arquivo_pdf_levantamento_prioridades_paa
from sme_ptrf_apps.paa.services.paa_service import PaaService

from sme_ptrf_apps.core.api.utils.pagination import CustomPagination
from sme_ptrf_apps.users.permissoes import (
    PermissaoAPITodosComLeituraOuGravacao,
    PermissaoApiUe
)
from sme_ptrf_apps.paa.api.serializers.paa_serializer import PaaSerializer
from sme_ptrf_apps.paa.models import Paa
from sme_ptrf_apps.core.models import Associacao

logger = logging.getLogger(__name__)


class PaaViewSet(WaffleFlagMixin, ModelViewSet):
    waffle_flag = "paa"
    permission_classes = [IsAuthenticated & PermissaoApiUe]
    lookup_field = 'uuid'
    queryset = Paa.objects.all()
    serializer_class = PaaSerializer
    pagination_class = CustomPagination
    http_method_names = ['get', 'post', 'delete']

    def get_queryset(self):
        qs = self.queryset
        associacao = self.request.query_params.get('associacao_uuid', None)

        if associacao is not None:
            qs = qs.filter(associacao=associacao)

        return qs

    @action(detail=False, methods=['get'], url_path='download-pdf-levantamento-prioridades',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def download_levantamento_prioridades_paa(self, request):
        associacao_uuid = self.request.query_params.get('associacao_uuid')
        associacao = Associacao.objects.filter(uuid=associacao_uuid).first()
        if associacao:
            nome_unidade = associacao.unidade.nome
            tipo_unidade = associacao.unidade.tipo_unidade
            associacao_nome = associacao.nome
        else:
            nome_unidade = None
            tipo_unidade = None
            associacao_nome = None

        dados = {
            "nome_associacao": associacao_nome,
            "nome_unidade": nome_unidade,
            "tipo_unidade": tipo_unidade,
            "username": request.user.username,
            "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "ano": datetime.now().year
        }
        return PaaService.gerar_arquivo_pdf_levantamento_prioridades_paa(dados)

    def destroy(self, request, *args, **kwargs):
        from django.db.models.deletion import ProtectedError

        obj = self.get_object()

        try:
            self.perform_destroy(obj)
        except ProtectedError:
            content = {
                'erro': 'ProtectedError',
                'mensagem': 'Este PAA não pode ser excluído porque já está sendo usado na aplicação.'
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_204_NO_CONTENT)
