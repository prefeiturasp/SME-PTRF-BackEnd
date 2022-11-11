import logging

from rest_framework import mixins, status
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated
from sme_ptrf_apps.users.permissoes import PermissaoApiDre, PermissaoAPIApenasDreComLeituraOuGravacao
from ...models.analise_consolidado_dre import AnaliseConsolidadoDre
from ..serializers.analise_consolidado_dre_serializer import AnaliseConsolidadoDreRetriveSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)


class AnalisesConsolidadoDreViewSet(
        mixins.RetrieveModelMixin,
        mixins.ListModelMixin,
        GenericViewSet
    ):
    permission_classes = [IsAuthenticated & PermissaoApiDre]
    lookup_field = 'uuid'
    queryset = AnaliseConsolidadoDre.objects.all()
    serializer_class = AnaliseConsolidadoDreRetriveSerializer

    # @action(
    #     detail=False,
    #     methods=['get'],
    #     url_path='info-para-documentos-consilidado-resumo',
    #     permission_classes=[IsAuthenticated & PermissaoAPIApenasDreComLeituraOuGravacao]
    # )

    # def info_para_documentos_consilidado_resumo(self, request):
    #     analise_atual_consolidado_uuid = request.query_params.get('analise_atual_consolidado_uuid')

    #     result = ResumoDocumentoConsolidado(
    #         analise_atual_consolidado_uuid=analise_atual_consolidado_uuid
    #     ).pegar_todas_informacoes_analise_documento()

    #     return Response(result, status=status.HTTP_200_OK)
