from rest_framework import status
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from django.http import Http404

import django_filters
from waffle.mixins import WaffleFlagMixin

from sme_ptrf_apps.paa.enums import RecursoOpcoesEnum, TipoAplicacaoOpcoesEnum
from sme_ptrf_apps.core.api.utils.pagination import CustomPagination
from sme_ptrf_apps.paa.models import PrioridadePaa
from sme_ptrf_apps.paa.models.prioridade_paa import SimNaoChoices
from sme_ptrf_apps.paa.api.serializers import (
    PrioridadePaaCreateUpdateSerializer,
    PrioridadePaaListSerializer
)
from sme_ptrf_apps.users.permissoes import PermissaoApiUe, PermissaoAPITodosComGravacao
from sme_ptrf_apps.paa.querysets import queryset_prioridades_paa


class PrioridadePaaViewSet(WaffleFlagMixin, ModelViewSet):
    waffle_flag = "paa"
    permission_classes = [PermissaoApiUe]
    lookup_field = 'uuid'
    queryset = PrioridadePaa.objects.all()
    serializer_class = PrioridadePaaCreateUpdateSerializer
    http_method_names = ["get", "post", "patch", "delete"]
    pagination_class = CustomPagination
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filterset_fields = (
        'acao_associacao__uuid',
        'paa__uuid',
        'recurso',
        'prioridade',  # 0 (False) ou 1 (True)
        'programa_pdde__uuid',
        'acao_pdde__uuid',
        'tipo_aplicacao',
        'tipo_despesa_custeio__uuid',
        'especificacao_material__uuid',
    )

    def get_queryset(self):
        qs = super().get_queryset()
        qs = queryset_prioridades_paa(qs)

        return qs

    def get_serializer_class(self):
        if self.action == 'list':
            return PrioridadePaaListSerializer
        else:
            return PrioridadePaaCreateUpdateSerializer

    @action(detail=False, methods=['get'], url_path='tabelas',
            permission_classes=[PermissaoApiUe])
    def tabelas(self, request, *args, **kwrgs):
        tabelas = dict(
            prioridades=SimNaoChoices.to_dict(),
            recursos=RecursoOpcoesEnum.to_dict(),
            tipos_aplicacao=TipoAplicacaoOpcoesEnum.to_dict(),
        )

        return Response(tabelas, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='excluir-lote',
            permission_classes=[PermissaoApiUe & PermissaoAPITodosComGravacao])
    def excluir_em_lote(self, request, *args, **kwargs):
        """
        Exclui em lote as prioridades de PAA.

        Essa action pode ser usada para excluir em lote as prioridades de PAA.

        - lista_uuids: lista de uuids das prioridades a serem excluídas.

        Retorna um dicionário com as informações dos erros e a mensagem
        de sucesso ou erro.
        """
        lista_uuids = request.data.get('lista_uuids', [])

        if not len(lista_uuids):
            content = {
                'erro': 'Falta de informações',
                'mensagem': 'É necessário enviar a lista de uuids a serem excluídos (lista_uuids).'
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        try:
            erros = PrioridadePaa.excluir_em_lote(lista_uuids)
            if len(erros):
                mensagem = 'Alguma das prioridades selecionadas já foi removida.'
            else:
                mensagem = 'Prioridades removidas com sucesso.'
            return Response({
                'erros': erros,
                'mensagem': mensagem
            }, status=status.HTTP_200_OK)

        except Exception as err:
            error = {
                'erro': "Falha ao excluir Prioridades em lote",
                'mensagem': str(err)
            }
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        """
        Cenário de exceção: quando tentar atualizar uma prioridade que já foi removida
        """
        try:
            self.get_object()
            return super().update(request, *args, **kwargs)
        except (Http404, NotFound):
            return Response(
                {"mensagem": "Prioridade não encontrada ou já foi removida da base de dados."},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'], url_path='duplicar')
    def duplicar(self, request, uuid=None):
        """
        Duplicar uma PrioridadePaa existente, criando um novo registro com os mesmos dados.
        O campo `valor_total` não informado
        """
        try:
            original = self.get_object()
        except (Http404, NotFound):
            return Response(
                {"mensagem": "Prioridade não encontrada ou já foi removida da base de dados."},
                status=status.HTTP_404_NOT_FOUND
            )

        original_data = {
            'paa': str(original.paa.uuid) if original.paa else None,
            'prioridade': int(original.prioridade),
            'recurso': original.recurso,
            'acao_associacao': str(original.acao_associacao.uuid) if original.acao_associacao else None,
            'programa_pdde': str(original.programa_pdde.uuid) if original.programa_pdde else None,
            'acao_pdde': str(original.acao_pdde.uuid) if original.acao_pdde else None,
            'tipo_aplicacao': original.tipo_aplicacao,
            'tipo_despesa_custeio': str(original.tipo_despesa_custeio.uuid) if original.tipo_despesa_custeio else None,
            'especificacao_material': (
                str(original.especificacao_material.uuid) if original.especificacao_material else None),
            'valor_total': None,
            'copia_de': str(original.uuid),
        }
        original_data = {k: v for k, v in original_data.items() if v is not None}

        serializer = PrioridadePaaCreateUpdateSerializer(data=original_data)

        serializer.is_valid(raise_exception=True)
        nova_prioridade = serializer.save()

        return Response(PrioridadePaaCreateUpdateSerializer(nova_prioridade).data, status=status.HTTP_201_CREATED)
