from django.db import transaction
from django.db.models.query_utils import Q

from drf_spectacular.utils import extend_schema, inline_serializer, OpenApiParameter, OpenApiTypes

from rest_framework import mixins, status
from rest_framework.decorators import action

from rest_framework.permissions import IsAuthenticated

from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response

from sme_ptrf_apps.core.choices.filtro_informacoes_associacao import FiltroInformacoesAssociacao

from ..serializers.acao_serializer import AcaoSerializer
from ...models import Acao, Recurso
from ...services import associacoes_nao_vinculadas_a_acao
from ..serializers.associacao_serializer import AssociacaoListSerializer
from rest_framework import serializers


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
        recurso_uuid = self.request.query_params.get('recurso_uuid')

        if nome is not None:
            qs = qs.filter(nome__unaccent__icontains=nome)

        if recurso_uuid is not None:
            recurso = Recurso.objects.filter(uuid=recurso_uuid).first()
            try:
                qs = qs.filter(recurso=recurso)
            except Recurso.DoesNotExist:
                return Response({'detail': 'Recurso não encontrado.'}, status=status.HTTP_400_BAD_REQUEST)

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
        responses={200: AcaoSerializer(many=True)},
        summary='Retorna as ações cujo recurso é marcado como legado.',
    )
    @action(detail=False, methods=['get'], url_path='acoes-recurso-legado')
    def acoes_ptrf(self, request):
        qs = Acao.objects.filter(recurso__legado=True).order_by('nome')
        return Response(AcaoSerializer(qs, many=True).data, status=status.HTTP_200_OK)

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
        recurso_uuid = self.request.query_params.get('recurso_uuid')

        encerradas = FiltroInformacoesAssociacao.FILTRO_INFORMACOES_ENCERRADAS
        nao_encerradas = FiltroInformacoesAssociacao.FILTRO_INFORMACOES_NAO_ENCERRADAS

        if recurso_uuid:
            qs = associacoes_nao_vinculadas_a_acao(acao, recurso_uuid=recurso_uuid)
        else:
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
        recurso_uuid = self.request.query_params.get('recurso_uuid')

        encerradas = FiltroInformacoesAssociacao.FILTRO_INFORMACOES_ENCERRADAS
        nao_encerradas = FiltroInformacoesAssociacao.FILTRO_INFORMACOES_NAO_ENCERRADAS

        if recurso_uuid:
            qs = associacoes_nao_vinculadas_a_acao(acao, recurso_uuid=recurso_uuid)
        else:
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

    @extend_schema(
        summary='Atualiza a ordem de exibição das ações',
        request=inline_serializer(
            name='ReordenarAcoesSerializer',
            fields={
                'uuids_ordenados': serializers.ListField(
                    child=serializers.UUIDField(),
                    help_text='Lista de UUIDs das ações na nova ordem de exibição.'
                )
            }
        ),
        responses={
            200: inline_serializer(
                name='ReordenarAcoesResponseSerializer',
                fields={'mensagem': serializers.CharField()}
            ),
            400: inline_serializer(
                name='ReordenarAcoesErrorSerializer',
                fields={'erro': serializers.CharField()}
            )
        }
    )
    @action(detail=False, methods=['post'], url_path='reordenar')
    def reordenar(self, request):
        uuids_ordenados = request.data.get('uuids_ordenados', [])

        if not uuids_ordenados:
            return Response(
                {'erro': 'A lista de UUIDs não foi fornecida.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Mapeia as Ações existentes por UUID para acesso O(1)
        # Assumindo que você criou o campo 'ordem_exibicao' ou usará 'posicao_nas_pesquisas'
        acoes = Acao.objects.filter(uuid__in=uuids_ordenados)
        acoes_dict = {str(acao.uuid): acao for acao in acoes}

        acoes_para_atualizar = []

        # Itera sobre a lista recebida para definir a nova ordem
        for posicao, uuid_str in enumerate(uuids_ordenados, start=1):
            acao = acoes_dict.get(str(uuid_str))
            if acao:
                acao.ordem_exibicao = posicao  # Ou atualiza o campo desejado
                acoes_para_atualizar.append(acao)

        if not acoes_para_atualizar:
            return Response(
                {'erro': 'Nenhuma ação correspondente foi encontrada.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Atualiza em lote com transação atômica para garantir consistência
        with transaction.atomic():
            Acao.objects.bulk_update(acoes_para_atualizar, ['ordem_exibicao'])

        return Response(
            {'mensagem': 'Ordem das ações atualizada com sucesso!'}, 
            status=status.HTTP_200_OK
        )

    @extend_schema(
        summary='Retorna as ações ordenadas pela ordem de exibição',
        description='Retorna a lista de ações ordenadas por recurso e por ordem_exibicao. Aceita filtro opcional por recurso_uuid.',
        parameters=[
            OpenApiParameter(
                name='recurso_uuid',
                description='UUID do recurso para filtrar as ações',
                required=False,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY
            ),
        ],
        responses={200: AcaoSerializer(many=True)},
    )
    @action(detail=False, methods=['get'], url_path='ordenadas')
    def acoes_ordenadas(self, request):
        """
        Retorna as ações ordenadas explicitamente por ordem_exibicao.
        Permite filtrar por um recurso específico através da query string 'recurso_uuid'.
        """
        qs = Acao.objects.all()
        recurso_uuid = request.query_params.get('recurso_uuid')

        if recurso_uuid:
            qs = qs.filter(recurso__uuid=recurso_uuid)
        else:
            return Response(
                {'erro': 'O parâmetro recurso_uuid é obrigatório para esta operação.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Ordena primariamente pelo recurso e secundariamente pela ordem de exibição
        qs = qs.order_by('recurso', 'ordem_exibicao', 'nome')

        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)