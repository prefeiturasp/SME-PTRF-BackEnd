import logging

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from sme_ptrf_apps.core.api.serializers import NotificacaoSerializer
from sme_ptrf_apps.core.api.serializers.notificacao_serializer import TipoNotificacaoSerializer, RemetenteNotificacaoSerializer, CategoriatificacaoSerializer
from sme_ptrf_apps.core.models import Notificacao
from sme_ptrf_apps.core.services import formata_data

logger = logging.getLogger(__name__)

DEFAULT_PAGE = 1
DEFAULT_PAGE_SIZE = 10


class CustomPagination(PageNumberPagination):
    page = DEFAULT_PAGE
    page_size = DEFAULT_PAGE_SIZE
    page_size_query_param = 'page_size'

    def get_paginated_response(self, data):
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'page': int(self.request.GET.get('page', DEFAULT_PAGE)),
            'page_size': int(self.request.GET.get('page_size', self.page_size)),
            'results': data
        })


class NotificacaoViewSet(viewsets.ModelViewSet):
    lookup_field = "uuid"
    permission_classes = (IsAuthenticated,)
    queryset = Notificacao.objects.all()
    serializer_class = NotificacaoSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        qs = Notificacao.objects.filter(usuario=self.request.user).all().order_by("-criado_em")

        if self.request.query_params.get('lido'):
            qs = qs.filter(lido=(self.request.query_params.get('lido') == 'True'))

        if self.request.query_params.get('tipo'):
            qs = qs.filter(tipo__id=self.request.query_params.get('tipo'))

        if self.request.query_params.get('remetente'):
            qs = qs.filter(remetente__id=self.request.query_params.get('remetente'))

        if self.request.query_params.get('categoria'):
            qs = qs.filter(categoria__id=self.request.query_params.get('categoria'))

        data_inicio = self.request.query_params.get('data_inicio')
        data_fim = self.request.query_params.get('data_fim')

        if data_inicio is not None and data_fim is not None:
            qs = qs.filter(criado_em__range=[data_inicio, data_fim])

        return qs

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        lista = []
        result = None
        if page is not None:
            datas = sorted(set([p.criado_em.date() for p in page]), reverse=True)
            for data in datas:
                d = {"data": formata_data(data), "infos": NotificacaoSerializer([n for n in page if (
                    n.criado_em.year == data.year and n.criado_em.month == data.month and n.criado_em.day == data.day)], many=True).data}
                lista.append(d)

            result = self.get_paginated_response(lista).data
        else:
            datas = sorted(self.get_queryset().dates("criado_em", "day"), reverse=True)

            for data in datas:
                d = {"data": formata_data(data), "infos": NotificacaoSerializer(self.get_queryset().filter(criado_em__year=data.year,
                                                                                                           criado_em__month=data.month,
                                                                                                           criado_em__day=data.day), many=True).data}
                lista.append(d)
            result = lista

        return Response(result)

    @action(detail=False, methods=['get'], url_path='quantidade-nao-lidos')
    def quantidade_de_nao_lidos(self, request):
        quantidade_nao = Notificacao.objects.filter(lido=False).count()
        data = {
            "quantidade_nao_lidos": quantidade_nao
        }
        return Response(data)

    @action(detail=False, methods=['put'], url_path='marcar-lido')
    def marcar_como_lido_nao_lido(self, request):
        dado = self.request.data

        if not dado['uuid'] and dado['lido']:
            resultado = {
                'erro': 'Dados incompletos',
                'mensagem': 'uuid da notificao e marcação de notificação como lida ou não-lida são obrigatórios.'
            }

            status_code = status.HTTP_400_BAD_REQUEST
            logger.info('Erro: %r', resultado)

        try:
            notificacao = Notificacao.objects.filter(uuid=dado['uuid']).first()
            notificacao.lido = dado['lido']
            notificacao.save()
        except Exception as err:
            resultado = {
                'erro': 'Erro ao realizar atualização',
                'mensagem': str(err)
            }

            status_code = status.HTTP_400_BAD_REQUEST
            logger.info('Erro: %r', resultado)

        resultado = {
            'mensagem': 'Notificação atualizada com sucesso'
        }
        status_code = status.HTTP_200_OK

        return Response(resultado, status=status_code)

    @action(detail=False, url_path='tabelas')
    def tabelas(self, _):
        def get_valores_from(serializer):
            valores = serializer.Meta.model.get_valores()
            return serializer(valores, many=True).data if valores else []

        result = {
            'tipos_notificacao': get_valores_from(TipoNotificacaoSerializer),
            'remetentes': get_valores_from(RemetenteNotificacaoSerializer),
            'categorias': get_valores_from(CategoriatificacaoSerializer)
        }

        return Response(result)
