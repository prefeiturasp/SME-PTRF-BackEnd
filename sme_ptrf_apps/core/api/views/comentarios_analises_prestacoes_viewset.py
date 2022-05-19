from django_filters import rest_framework as filters
from django.core.exceptions import ValidationError
from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from sme_ptrf_apps.core.api.serializers import ComentarioAnalisePrestacaoRetrieveSerializer
from sme_ptrf_apps.core.models import ComentarioAnalisePrestacao, PrestacaoConta
from sme_ptrf_apps.users.permissoes import PermissaoAPITodosComLeituraOuGravacao


class ComentariosAnalisesPrestacoesViewSet(viewsets.ModelViewSet):
    lookup_field = 'uuid'
    permission_classes = [AllowAny]
    serializer_class = ComentarioAnalisePrestacaoRetrieveSerializer
    queryset = ComentarioAnalisePrestacao.objects.all().order_by('ordem')
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('prestacao_conta__uuid',)

    @action(detail=False, url_path='comentarios', methods=['get'],
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def comentarios_nao_notificados_e_notificados(self, request):

        prestacao_conta_uuid = request.query_params.get('prestacao_conta__uuid')

        if prestacao_conta_uuid is None:
            erro = {
                'erro': 'parametros_requerido',
                'mensagem': 'É necessário enviar o uuid da prestação de contas.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            prestacao_de_conta = PrestacaoConta.by_uuid(prestacao_conta_uuid)
        except (PrestacaoConta.DoesNotExist, ValidationError):
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto prestacao_conta para o uuid {prestacao_conta_uuid} não foi encontrado na base."
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        comentarios_nao_notificados = ComentarioAnalisePrestacao.objects.filter(notificado=False,
                                                                                prestacao_conta=prestacao_de_conta)
        comentarios_notificados = ComentarioAnalisePrestacao.objects.filter(notificado=True,
                                                                            prestacao_conta=prestacao_de_conta)

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
