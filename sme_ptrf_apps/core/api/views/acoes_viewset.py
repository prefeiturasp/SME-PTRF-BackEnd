from django.db.models.query_utils import Q

from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes

from rest_framework import mixins, status
from rest_framework.decorators import action

from rest_framework.permissions import IsAuthenticated

from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response

from sme_ptrf_apps.core.choices.filtro_informacoes_associacao import FiltroInformacoesAssociacao

from ..serializers.acao_serializer import AcaoSerializer
from ...models import Acao
from ...services import associacoes_nao_vinculadas_a_acao
from ..serializers.associacao_serializer import AssociacaoListSerializer


class AcoesViewSet(mixins.ListModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.CreateModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.DestroyModelMixin,
                   GenericViewSet):
    permission_classes = [IsAuthenticated]
    lookup_field = 'uuid'
    queryset = Acao.objects.all().order_by('nome')
    serializer_class = AcaoSerializer

    def get_queryset(self):
        qs = Acao.objects.all()

        nome = self.request.query_params.get('nome')
        if nome is not None:
            qs = qs.filter(nome__unaccent__icontains=nome)

        return qs.order_by('nome')

    @extend_schema(
        parameters=[
            OpenApiParameter(name='nome', description='nome da Ação', required=False,
                             type=OpenApiTypes.STR, location=OpenApiParameter.QUERY),
        ],
        responses={200: AcaoSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        from django.db.models.deletion import ProtectedError

        obj = self.get_object()

        try:
            self.perform_destroy(obj)
        except ProtectedError:
            content = {
                'erro': 'ProtectedError',
                'mensagem': 'Essa operação não pode ser realizada. Há associações vinculadas a esse tipo de ação.'
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        parameters=[
            OpenApiParameter(name='filtro_informacoes', description='Filtrar por informações. Separado por vírgula',
                             required=False, type=OpenApiTypes.STR, location=OpenApiParameter.QUERY),
        ],
        responses={200: AssociacaoListSerializer(many=True)},
    )
    @action(detail=True, methods=['get'], url_path='associacoes-nao-vinculadas')
    def associacoes_nao_vinculadas(self, request, uuid=None):
        acao = self.get_object()
        filtro_informacoes = self.request.query_params.get('filtro_informacoes')
        filtro_informacoes_list = filtro_informacoes.split(',') if filtro_informacoes else []

        encerradas = FiltroInformacoesAssociacao.FILTRO_INFORMACOES_ENCERRADAS
        nao_encerradas = FiltroInformacoesAssociacao.FILTRO_INFORMACOES_NAO_ENCERRADAS

        qs = associacoes_nao_vinculadas_a_acao(acao)

        if filtro_informacoes_list:
            if encerradas in filtro_informacoes_list and nao_encerradas in filtro_informacoes_list:
                qs = qs
            elif nao_encerradas in filtro_informacoes_list:
                qs = qs.filter(data_de_encerramento__isnull=True)

            elif encerradas in filtro_informacoes_list:
                qs = qs.filter(data_de_encerramento__isnull=False)

        result = AssociacaoListSerializer(qs, many=True).data
        return Response(result, status=status.HTTP_200_OK)

    @extend_schema(
        parameters=[
            OpenApiParameter(name='filtro_informacoes', description='Filtrar por informações. Separado por vírgula',
                             required=False, type=OpenApiTypes.STR, location=OpenApiParameter.QUERY),
        ],
        responses={200: AssociacaoListSerializer(many=True)},
    )
    @action(detail=True, methods=['get'], url_path='associacoes-nao-vinculadas-por-nome/(?P<nome>[^/.]+)')
    def associacoes_nao_vinculadas_por_nome(self, request, nome, uuid=None):
        acao = self.get_object()
        filtro_informacoes = self.request.query_params.get('filtro_informacoes')
        filtro_informacoes_list = filtro_informacoes.split(',') if filtro_informacoes else []

        encerradas = FiltroInformacoesAssociacao.FILTRO_INFORMACOES_ENCERRADAS
        nao_encerradas = FiltroInformacoesAssociacao.FILTRO_INFORMACOES_NAO_ENCERRADAS

        qs = associacoes_nao_vinculadas_a_acao(acao)

        if nome is not None:
            qs = qs.filter(Q(nome__unaccent__icontains=nome) | Q(
                unidade__nome__unaccent__icontains=nome) | Q(
                unidade__codigo_eol__icontains=nome))

        if filtro_informacoes_list:
            if encerradas in filtro_informacoes_list and nao_encerradas in filtro_informacoes_list:
                qs = qs
            elif nao_encerradas in filtro_informacoes_list:
                qs = qs.filter(data_de_encerramento__isnull=True)

            elif encerradas in filtro_informacoes_list:
                qs = qs.filter(data_de_encerramento__isnull=False)

        result = AssociacaoListSerializer(qs, many=True).data
        return Response(result, status=status.HTTP_200_OK)
