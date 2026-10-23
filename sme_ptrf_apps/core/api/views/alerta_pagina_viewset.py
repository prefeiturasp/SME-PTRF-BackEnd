from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from sme_ptrf_apps.core.api.serializers import (
    AlertaPaginaQueryParamsSerializer,
    AlertaPaginaResponseSerializer,
)
from sme_ptrf_apps.core.models import AlertaPagina
from sme_ptrf_apps.core.services import AlertaPaginaService


class AlertaPaginaViewset(viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = AlertaPagina.objects.none()
    serializer_class = AlertaPaginaResponseSerializer

    @extend_schema(
        parameters=[AlertaPaginaQueryParamsSerializer],
        responses={200: AlertaPaginaResponseSerializer},
    )
    @action(detail=False, methods=["get"], url_path="vigente")
    def vigente(self, request):
        parametros = AlertaPaginaQueryParamsSerializer(data=request.query_params)
        parametros.is_valid(raise_exception=True)

        dados = parametros.validated_data
        alerta = AlertaPaginaService.alerta_para_unidade(dados['unidade'], dados['recurso'], dados['categoria'])

        return Response(AlertaPaginaResponseSerializer({'alerta': alerta}).data)
