import logging
from waffle.mixins import WaffleFlagMixin
from rest_framework.exceptions import NotFound
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from drf_spectacular.utils import extend_schema_view
from sme_ptrf_apps.core.api.utils.pagination import CustomPagination
from sme_ptrf_apps.users.permissoes import (
    PermissaoApiDre
)
from sme_ptrf_apps.paa.models import Paa
from sme_ptrf_apps.paa.services.paa_dre_service import PaaDreService, ValidacaoPaaDre
from sme_ptrf_apps.paa.filters import PaaDreFilter

from .docs.paa_dre_docs import DOCS


logger = logging.getLogger(__name__)


@extend_schema_view(**DOCS)
class PaaDreViewSet(WaffleFlagMixin, GenericViewSet):
    waffle_flag = "paa-dre"
    permission_classes = [IsAuthenticated & PermissaoApiDre]
    pagination_class = CustomPagination
    queryset = Paa.objects.none()
    http_method_names = ['get']

    def list(self, request, *args, **kwargs):
        raise NotFound()

    def retrieve(self, request, pk=None):
        unidade_dre_uuid = pk

        filtro = PaaDreFilter(
            data=request.query_params,
            queryset=Paa.objects.none()
        )

        if not filtro.is_valid():
            return Response(filtro.errors, status=status.HTTP_400_BAD_REQUEST)

        filtros_tratados = filtro.form.cleaned_data

        try:
            data = PaaDreService.listar_paas(unidade_dre_uuid, filtros_tratados)

            page = self.paginate_queryset(data)

            if page is not None:
                return self.get_paginated_response(page)

            return Response(data)

        except ValidacaoPaaDre as erro:
            detail = erro.args[0] if erro.args else "Erro de validação"

            if not isinstance(detail, (dict, list, str)):
                detail = str(detail)

            return Response(detail, status=status.HTTP_400_BAD_REQUEST)
        except Exception as erro:
            return Response(str(erro), status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'], url_path='tabelas')
    def tabelas(self, request, pk=None):
        """
        Retorna dados auxiliares para filtros da listagem PAA DRE.
        """
        unidade_dre_uuid = pk

        data = PaaDreService.obter_tabelas(unidade_dre_uuid)

        return Response(data)
