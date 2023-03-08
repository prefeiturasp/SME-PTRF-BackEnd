import logging

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from sme_ptrf_apps.core.api.serializers import NotificacaoSerializer

from sme_ptrf_apps.core.models import Notificacao, Unidade, Periodo
from sme_ptrf_apps.core.services.notificacao_services import formata_data, notificar_comentario_pc
from django.core.exceptions import ValidationError

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
    permission_classes = [IsAuthenticated]
    queryset = Notificacao.objects.all()
    serializer_class = NotificacaoSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        qs = Notificacao.objects.filter(usuario=self.request.user).all().order_by("-criado_em")

        if self.request.query_params.get('lido'):
            qs = qs.filter(lido=(self.request.query_params.get('lido') == 'True'))

        if self.request.query_params.get('tipo'):
            qs = qs.filter(tipo=self.request.query_params.get('tipo'))

        if self.request.query_params.get('remetente'):
            qs = qs.filter(remetente=self.request.query_params.get('remetente'))

        if self.request.query_params.get('categoria'):
            qs = qs.filter(categoria=self.request.query_params.get('categoria'))

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
                    n.criado_em.year == data.year and n.criado_em.month == data.month and n.criado_em.day == data.day)],
                                                                                many=True).data}
                lista.append(d)

            result = self.get_paginated_response(lista).data
        else:
            datas = sorted(self.get_queryset().dates("criado_em", "day"), reverse=True)

            for data in datas:
                d = {"data": formata_data(data),
                     "infos": NotificacaoSerializer(self.get_queryset().filter(criado_em__year=data.year,
                                                                               criado_em__month=data.month,
                                                                               criado_em__day=data.day),
                                                    many=True).data}
                lista.append(d)
            result = lista

        return Response(result)

    @action(detail=False, methods=['get'], url_path='erro-concluir-pc')
    def erro_concluir_pc(self, request):
        resultado = Notificacao.objects.filter(usuario=self.request.user, categoria="ERRO_AO_CONCLUIR_PC").all().order_by("-criado_em")
        return Response(NotificacaoSerializer(resultado, many=True).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='quantidade-nao-lidos')
    def quantidade_de_nao_lidos(self, request):
        quantidade_nao = Notificacao.objects.filter(usuario=self.request.user).filter(lido=False).count()
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
        result = {
            'tipos_notificacao': Notificacao.tipos_to_json(),
            'remetentes': Notificacao.remetentes_to_json(),
            'categorias': Notificacao.categorias_to_json()
        }

        return Response(result)

    @action(detail=False, url_path="notificar", methods=['post'])
    def notificar(self, request):
        dado = self.request.data

        if not dado.get('associacao') or not dado.get('periodo') or not dado.get('comentarios'):
            resultado = {
                'erro': 'Dados incompletos',
                'mensagem': 'uuid da associação, do período e lista uuids de comentários são obrigatórios.'
            }

            status_code = status.HTTP_400_BAD_REQUEST
            logger.info('Erro: %r', resultado)
            return Response(resultado, status=status_code)

        try:
            notificar_comentario_pc(dado)
        except Exception as err:
            logger.info("Erro no processo de notificação: %s", str(err))
            resultado = {
                'erro': 'Problema no processo de notificar usuário',
                'mensagem': "Erro no processo de notificacao"
            }
            return Response(resultado, status=status.HTTP_400_BAD_REQUEST)

        return Response({"mensagem": "Processo de notificação enviado com sucesso."})

    @action(detail=False, url_path="notificar-comentarios-de-analise-consolidado-dre", methods=['post'])
    def notificar_comentarios_de_analise_consolidado_dre(self, request):

        from sme_ptrf_apps.dre.services.notificacao_service.class_notificacao_comentario_de_analise_consolidado_dre import \
            NotificacaoComentarioDeAnaliseConsolidadoDre

        dado = self.request.data

        if not dado.get('dre') or not dado.get('periodo') or not dado.get('comentarios'):
            resultado = {
                'erro': 'Dados incompletos',
                'mensagem': 'uuid da dre, do período e lista uuids de comentários são obrigatórios.'
            }

            status_code = status.HTTP_400_BAD_REQUEST
            logger.info('Erro: %r', resultado)
            return Response(resultado, status=status_code)

        comentarios = dado.get('comentarios')

        try:
            dre = Unidade.by_uuid(dado['dre'])
        except (Unidade.DoesNotExist, ValidationError):
            resultado = {
                'erro': 'objeto_nao_encontrado',
                'mensagem': f"O objeto DRE para o uuid {dado.get('dre')} não foi encontrado na base"
            }
            status_code = status.HTTP_400_BAD_REQUEST
            logger.info('Erro: %r', resultado)
            return Response(resultado, status=status_code)

        try:
            periodo = Periodo.by_uuid(dado['periodo'])
        except (Periodo.DoesNotExist, ValidationError):
            resultado = {
                'erro': 'objeto_nao_encontrado',
                'mensagem': f"O objeto Periodo para o uuid {dado.get('periodo')} não foi encontrado na base"
            }
            status_code = status.HTTP_400_BAD_REQUEST
            logger.info('Erro: %r', resultado)
            return Response(resultado, status=status_code)

        try:
            notificacao_enviada = NotificacaoComentarioDeAnaliseConsolidadoDre(
                dre=dre,
                periodo=periodo,
                comentarios=comentarios,
                enviar_email=True
            ).notificar()

        except Exception as err:
            logger.info("Erro no processo de notificação: %s", str(err))
            resultado = {
                'erro': 'Problema no processo de notificar usuário',
                'mensagem': "Erro no processo de notificacao"
            }
            return Response(resultado, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({"mensagem": "Processo de notificação finalizado.", "enviada": notificacao_enviada}, status=status.HTTP_200_OK)
