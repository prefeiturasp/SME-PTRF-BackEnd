"""
Módulo de API para gerenciamento dos programas PDDE.

Este módulo concentra os endpoints de listar, criar, atualizar,
remover, somar o total por programas e consultar programas do PDDE.
"""
from rest_framework import status, serializers
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter

import django_filters

from waffle.mixins import WaffleFlagMixin

from sme_ptrf_apps.paa.models import ProgramaPdde
from sme_ptrf_apps.paa.services import PaaService

from sme_ptrf_apps.paa.api.serializers import ProgramaPddeSerializer, ProgramasPddeSomatorioTotalSerializer
from sme_ptrf_apps.core.api.utils.pagination import CustomPagination

from sme_ptrf_apps.users.permissoes import PermissaoAPIApenasSmeComLeituraOuGravacao, PermissaoApiUe
from drf_spectacular.utils import extend_schema_view
from .docs.programas_pdde_docs import DOCS


class ProgramaPddeFiltro(django_filters.FilterSet):
    """
    Defina os filtros disponíveis para consulta de programas do PDDE.

    Permite filtrar programas pelo nome utilizando uma busca parcial.
    """
    nome = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = ProgramaPdde
        fields = ['nome', ]


@extend_schema_view(**DOCS)
class ProgramaPddeViewSet(WaffleFlagMixin, ModelViewSet):
    """
    ViewSet responsável pelo gerenciamento dos programas do PDDE.

    Permite listar, criar, atualizar, remover, somar o total
    por programas e consultar programas do PDDE, com suporte à
    filtragem e paginação dos resultados.
    """
    waffle_flag = "paa"
    permission_classes = [IsAuthenticated & PermissaoAPIApenasSmeComLeituraOuGravacao]
    lookup_field = 'uuid'
    queryset = ProgramaPdde.objects.all().order_by('nome')
    serializer_class = ProgramaPddeSerializer
    pagination_class = CustomPagination
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filterset_class = ProgramaPddeFiltro

    def validar_campos(self, request) -> str:
        """
        Valide os campos obrigatórios da requisição.

        Verifica se o campo ``nome`` foi informado. Caso contrário, lança uma
        exceção de validação.

        Args:
            request: Requisição contendo os dados enviados pelo cliente.

        Returns:
            str: Nome do programa informado na requisição.

        Raises:
            serializers.ValidationError: Se o campo ``nome`` não for informado.
        """
        nome = request.data.get('nome')
        if not nome:
            raise serializers.ValidationError(
                {"nome": "Nome do Programa PDDE não foi informado."}
            )
        return nome

    def create(self, request) -> Response:
        """ Método acionado antes do validate do Serializer para
            validação de constraints da Model (ao Criar)"""

        nome = self.validar_campos(request)
        if ProgramaPdde.objects.filter(nome__iexact=nome).first():
            raise serializers.ValidationError(
                {
                    "erro": "Duplicated",
                    "detail": ("Erro ao criar Programa PDDE. Já existe um " +
                               "Programa PDDE cadastrado com este nome.")
                }
            )
        return super().create(request)

    def update(self, request, *args, **kwargs) -> Response:
        """ Método acionado antes do validate do Serializer
            para validação de constraints da Model (Ao Atualizar)"""

        obj = self.get_object()
        nome = request.data.get('nome')
        if ProgramaPdde.objects.exclude(pk=obj.pk).filter(nome__iexact=nome).first():
            raise serializers.ValidationError(
                {
                    "erro": "Duplicated",
                    "detail": ("Erro ao atualizar Programa PDDE. Já existe um " +
                               "Programa PDDE cadastrado com este nome.")
                }
            )

        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs) -> Response:
        """
        Exclua um programa do PDDE.

        A exclusão é permitida apenas quando o programa não possui ações
        vinculadas. Caso existam vínculos, retorna uma resposta com erro
        informando que a exclusão não pode ser realizada.

        Args:
            request: Requisição HTTP.
            *args: Argumentos posicionais adicionais.
            **kwargs: Argumentos nomeados adicionais.

        Returns:
            Response: Resposta HTTP com status 204 em caso de sucesso ou
                400 quando o programa possui ações vinculadas.
        """
        obj = self.get_object()

        if obj.acaopdde_set.count() > 0:
            content = {
                'erro': 'ProtectedError',
                'mensagem': ("Não é possível excluir. " +
                             "Este programa ainda está vinculado há alguma ação.")
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        self.perform_destroy(obj)

        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        parameters=[
            OpenApiParameter(name='paa_uuid', description='UUID do PAA', required=True,
                             type=OpenApiTypes.UUID, location=OpenApiParameter.QUERY),
        ],
        responses={200: OpenApiTypes.OBJECT},
        description="Retornam os totais por programa PDDE relacionados a um PAA"
    )
    @action(detail=False, methods=['get'], url_path='totais',
            permission_classes=[IsAuthenticated & PermissaoApiUe])
    def somatorio_total_por_programas(self, request) -> Response:
        """
        Retorne o somatório dos valores por programa PDDE para um PAA.

        Obtém o identificador do PAA por meio do parâmetro ``paa_uuid`` da
        requisição. Caso o parâmetro não seja informado, lança uma exceção de
        validação.

        Args:
            request: Requisição HTTP contendo o parâmetro ``paa_uuid``.

        Returns:
            Response: Resposta HTTP com o somatório dos valores por programa
                PDDE.

        Raises:
            serializers.ValidationError: Se o parâmetro ``paa_uuid`` não for
                informado.
        """
        paa = request.query_params.get('paa_uuid')
        if not paa:
            raise serializers.ValidationError({
                'erro': 'NotFound',
                'mensagem': "PAA não foi informado."
            })

        response = PaaService.somatorio_totais_por_programa_pdde(paa)
        serializer = ProgramasPddeSomatorioTotalSerializer(response)
        return Response(serializer.data, status=status.HTTP_200_OK)
