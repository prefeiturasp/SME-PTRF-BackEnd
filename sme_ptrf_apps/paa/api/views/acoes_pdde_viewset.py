from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.deletion import ProtectedError
import django_filters
from waffle.mixins import WaffleFlagMixin

from sme_ptrf_apps.paa.models import AcaoPdde, ReceitaPrevistaPdde, Paa, PeriodoPaa
from ..serializers.acao_pdde_serializer import AcaoPddeSerializer
from ..serializers.receita_prevista_pdde_serializer import ReceitasPrevistasPDDEValoresSerializer

from ....core.api.utils.pagination import CustomPagination

from sme_ptrf_apps.users.permissoes import PermissaoAPIApenasSmeComLeituraOuGravacao, PermissaoApiUe


class AcaoPddeFiltro(django_filters.FilterSet):
    nome = django_filters.CharFilter(lookup_expr='icontains')
    programa__uuid = django_filters.CharFilter(field_name="programa__uuid", lookup_expr="exact")
    programa__nome = django_filters.CharFilter(field_name="programa__nome", lookup_expr="icontains")
    aceita_capital = django_filters.BooleanFilter()
    aceita_custeio = django_filters.BooleanFilter()
    aceita_livre_aplicacao = django_filters.BooleanFilter()

    class Meta:
        model = AcaoPdde
        fields = [
            'nome',
            'programa__uuid',
            'programa__nome',
            'aceita_capital',
            'aceita_custeio',
            'aceita_livre_aplicacao'
        ]


class AcoesPddeViewSet(WaffleFlagMixin, ModelViewSet):
    waffle_flag = "paa"
    permission_classes = [IsAuthenticated, PermissaoAPIApenasSmeComLeituraOuGravacao]
    lookup_field = 'uuid'
    queryset = AcaoPdde.objects.all().filter(status=AcaoPdde.STATUS_ATIVA).order_by('nome')
    serializer_class = AcaoPddeSerializer
    pagination_class = CustomPagination
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filterset_class = AcaoPddeFiltro

    @extend_schema(
        parameters=[
            OpenApiParameter(name='paa_uuid', description='UUID do PAA', required=True,
                             type=OpenApiTypes.UUID, location=OpenApiParameter.QUERY),
        ],
        responses={200: OpenApiTypes.OBJECT},
        description="Retornam as receitas previstas PDDE das Ações PDDE de um PAA"
    )
    @action(detail=False, methods=['get'], url_path='receitas-previstas-pdde',
            permission_classes=[IsAuthenticated & PermissaoApiUe])
    def receitas_previstas_pdde(self, request):

        paa_uuid = self.request.query_params.get('paa_uuid')
        if not paa_uuid:
            raise serializers.ValidationError({"non_field_errors": "PAA não foi informado."})

        # Lista ações PDDE com os totais de receitas previstas PDDE de acordo com o PAA
        qs_acoes_pdde = AcaoPdde.objects.filter(status=AcaoPdde.STATUS_ATIVA)

        # Paginação na action
        page = self.paginate_queryset(qs_acoes_pdde)
        serializer = self.get_serializer(page, many=True)

        # Adicionar dados extras aos dados serializados
        for serial_acao_pdde in serializer.data:
            qs_receitas_pdde = ReceitaPrevistaPdde.objects.filter(
                acao_pdde__uuid=serial_acao_pdde.get('uuid'),
                paa__uuid=paa_uuid
            ).first()

            serial_acao_pdde['receitas_previstas_pdde_valores'] = ReceitasPrevistasPDDEValoresSerializer(
                qs_receitas_pdde).data

        if page is not None:
            return self.get_paginated_response(serializer.data)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def valida_campos(self, request):
        nome = request.data.get('nome')
        programa = request.data.get('programa')
        if not nome:
            raise serializers.ValidationError(
                {"nome": "Nome da ação PDDE não foi informado."}
            )
        if not programa:
            raise serializers.ValidationError(
                {"programa": "O Programa PDDE não foi informado."}
            )
        return nome, programa

    def create(self, request):
        """ Método acionado antes do validate do Serializer para validação de
            constraints da Model (ao Criar)"""
        nome, programa = self.valida_campos(request)

        try:
            AcaoPdde.objects.get(nome=nome, programa__uuid=programa)
            raise serializers.ValidationError({
                "erro": "Duplicated",
                "detail": ("Erro ao criar Ação PDDE. Já existe uma Ação PDDE "
                           "cadastrada com este nome e programa.")
            })
        except AcaoPdde.DoesNotExist:
            # Não existe nenhuma Ação PDDE cadastrada com o nome e programa informados,
            # ao criar uma ação PDDE
            pass
        return super().create(request)

    def update(self, request, *args, **kwargs):
        """ Método acionado antes do validate do Serializer para validação de
            constraints da Model (Ao Atualizar)"""
        obj = self.get_object()
        nome, programa = self.valida_campos(request)

        try:
            AcaoPdde.objects.exclude(pk=obj.pk).get(nome=nome, programa__uuid=programa)
            raise serializers.ValidationError({
                "erro": "Duplicated",
                "detail": ("Erro ao atualizar Ação PDDE. Já existe uma "
                           "Ação PDDE cadastrada com este nome e programa.")
            })
        except AcaoPdde.DoesNotExist:
            # Não existe nenhuma Ação PDDE cadastrada com o nome e programa informados,
            # ao atualizar uma Ação PDDE
            pass
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """ Método para inativar uma Ação PDDE com validações específicas """
        try:
            obj = self.get_object()
            periodo_vigente = PeriodoPaa.periodo_vigente()
            receitas_previstas_periodo_vigente = obj.receitaprevistapdde_set.filter(paa__periodo_paa=periodo_vigente).exists()
        
            if receitas_previstas_periodo_vigente:
                return Response(
                    {"detail": "Esta ação PDDE não pode ser excluída porque está sendo utilizada em um Plano Anual de Atividades (PAA)."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                return super().destroy(request, *args, **kwargs)
        except ProtectedError:
            obj.status = AcaoPdde.STATUS_INATIVA
            obj.save()
            
            content = {
                'erro': 'ProtectedError',
                'mensagem': 'Ação PDDE excluída com sucesso.'
            }
            return Response(content, status=status.HTTP_204_NO_CONTENT)
        except (Http404, ObjectDoesNotExist, AcaoPdde.DoesNotExist):
            return Response(
                {"detail": "Ação PDDE não encontrada."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"detail": f"Erro ao inativar Ação PDDE: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )