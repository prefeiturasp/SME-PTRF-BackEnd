from django_filters import rest_framework as filters
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from sme_ptrf_apps.core.api.serializers import ComentarioAnalisePrestacaoRetrieveSerializer
from sme_ptrf_apps.core.models import ComentarioAnalisePrestacao


class ComentariosAnalisesPrestacoesViewSet(viewsets.ModelViewSet):
    lookup_field = 'uuid'
    permission_classes = [AllowAny]
    serializer_class = ComentarioAnalisePrestacaoRetrieveSerializer
    queryset = ComentarioAnalisePrestacao.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('prestacao_conta__uuid',)

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
