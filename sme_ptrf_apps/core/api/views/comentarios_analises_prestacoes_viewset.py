from django_filters import rest_framework as filters
from django.db.models import Q
from django.core.exceptions import ValidationError
from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from sme_ptrf_apps.core.api.serializers import ComentarioAnalisePrestacaoRetrieveSerializer
from sme_ptrf_apps.core.models import ComentarioAnalisePrestacao, PrestacaoConta, Associacao, Periodo
from sme_ptrf_apps.users.permissoes import PermissaoAPITodosComLeituraOuGravacao


class ComentariosAnalisesPrestacoesViewSet(viewsets.ModelViewSet):
    lookup_field = 'uuid'
    permission_classes = [AllowAny]
    serializer_class = ComentarioAnalisePrestacaoRetrieveSerializer
    queryset = ComentarioAnalisePrestacao.objects.all().order_by('ordem')
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('prestacao_conta__uuid',)

    def destroy(self, request, *args, **kwargs):
        comentario = self.get_object()
        if comentario.notificado:
            erro = {
                'erro': 'comentario_ja_notificado',
                'mensagem': 'Comentários já notificados não podem mais ser editados ou removidos.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            self.perform_destroy(comentario)
        except Exception as err:
            erro = {
                'erro': 'comentario_nao_excluido',
                'mensagem': str(err)
            }
            return Response(erro, status=status.HTTP_404_NOT_FOUND)

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, url_path='comentarios', methods=['get'],
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def comentarios_nao_notificados_e_notificados(self, request):
        prestacao_conta_uuid = request.query_params.get('prestacao_conta__uuid')
        associacao_uuid = request.query_params.get('associacao_uuid')
        periodo_uuid = request.query_params.get('periodo_uuid')

        prestacao_de_conta = None
        associacao = None
        periodo = None

        if not (prestacao_conta_uuid or (associacao_uuid and periodo_uuid)):
            erro = {
                'erro': 'parametros_requerido',
                'mensagem': 'É necessário enviar o uuid da prestação de contas ou o uuid da associação e o uuid do período.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        if prestacao_conta_uuid:
            try:
                prestacao_de_conta = PrestacaoConta.by_uuid(prestacao_conta_uuid)
            except (PrestacaoConta.DoesNotExist, ValidationError):
                erro = {
                    'erro': 'Objeto não encontrado.',
                    'mensagem': f"O objeto prestacao_conta para o uuid {prestacao_conta_uuid} não foi encontrado na base."
                }
                return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        if associacao_uuid and periodo_uuid:
            try:
                associacao = Associacao.by_uuid(associacao_uuid)
            except (Associacao.DoesNotExist, ValidationError):
                erro = {
                    'erro': 'Objeto não encontrado.',
                    'mensagem': f"O objeto associacao para o uuid {associacao_uuid} não foi encontrado na base."
                }
                return Response(erro, status=status.HTTP_400_BAD_REQUEST)

            try:
                periodo = Periodo.by_uuid(periodo_uuid)
            except (Periodo.DoesNotExist, ValidationError):
                erro = {
                    'erro': 'Objeto não encontrado.',
                    'mensagem': f"O objeto periodo para o uuid {periodo_uuid} não foi encontrado na base."
                }
                return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        if prestacao_de_conta:
            comentarios_nao_notificados = ComentarioAnalisePrestacao.objects.filter(
                notificado=False,
                prestacao_conta=prestacao_de_conta
            ).order_by('ordem')

            comentarios_notificados = ComentarioAnalisePrestacao.objects.filter(
                notificado=True,
                prestacao_conta=prestacao_de_conta
            ).order_by('-notificado_em')
        elif associacao and periodo:
            comentarios_nao_notificados = ComentarioAnalisePrestacao.objects.filter(
                Q(associacao=associacao) & Q(periodo=periodo),
                notificado=False
            ).order_by('ordem')

            comentarios_notificados = ComentarioAnalisePrestacao.objects.filter(
                Q(associacao=associacao) & Q(periodo=periodo),
                notificado=True,
            ).order_by('-notificado_em')
        else:
            comentarios_nao_notificados = list()
            comentarios_notificados = list()

        result = {
            'comentarios_nao_notificados': self.serializer_class(comentarios_nao_notificados, many=True).data,
            'comentarios_notificados': self.serializer_class(comentarios_notificados, many=True).data
        }

        return Response(result)

    @action(detail=False, methods=['patch'], url_path='reordenar-comentarios')
    def reordenar_comentarios(self, request):
        comentarios_de_analise = request.data.get('comentarios_de_analise', None)
        if comentarios_de_analise is None:
            response = {
                'erro': 'falta_de_informacoes',
                'operacao': 'reordenar-comentarios',
                'mensagem': 'Faltou informar o campo comentarios_de_analise no payload.'
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        try:
            ComentarioAnalisePrestacao.reordenar_comentarios(novas_ordens_comentarios=comentarios_de_analise)
        except ComentarioAnalisePrestacao.DoesNotExist:
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"Algum comentário da lista não foi encontrado pelo uuid informado."
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        response = {
            'operacao': 'reordenar-comentarios',
            'mensagem': 'Ordenação de mensagens concluída com sucesso.'
        }
        return Response(response, status=status.HTTP_200_OK)
