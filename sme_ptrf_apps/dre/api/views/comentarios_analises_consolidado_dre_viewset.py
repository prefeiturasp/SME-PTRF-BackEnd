from django_filters import rest_framework as filters
from django.core.exceptions import ValidationError
from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from sme_ptrf_apps.users.permissoes import PermissaoAPIApenasSmeComLeituraOuGravacao
from ..serializers.comentario_analise_consolidado_dre_serializer import ComentarioAnaliseConsolidadoDRESerializer
from ...models.comentario_analise_consolidado_dre import ComentarioAnaliseConsolidadoDRE
from ...models.consolidado_dre import ConsolidadoDRE


class ComentariosAnalisesConsolidadosDREViewSet(viewsets.ModelViewSet):
    lookup_field = 'uuid'
    permission_classes = [AllowAny]
    serializer_class = ComentarioAnaliseConsolidadoDRESerializer
    queryset = ComentarioAnaliseConsolidadoDRE.objects.all().order_by('ordem')
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('consolidado_dre__uuid',)

    @action(detail=False, url_path='comentarios', methods=['get'],
            permission_classes=[IsAuthenticated & PermissaoAPIApenasSmeComLeituraOuGravacao])
    def comentarios_nao_notificados_e_notificados(self, request):
        consolidado_dre_uuid = request.query_params.get('consolidado_dre')

        if consolidado_dre_uuid is None:
            erro = {
                'erro': 'parametros_requerido',
                'mensagem': 'É necessário enviar o uuid do Consolidado DRE.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            consolidado_dre = ConsolidadoDRE.by_uuid(consolidado_dre_uuid)
        except (ConsolidadoDRE.DoesNotExist, ValidationError):
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto Consolidado DRE para o uuid {consolidado_dre_uuid} não foi encontrado na base."
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        comentarios_nao_notificados = ComentarioAnaliseConsolidadoDRE.objects.filter(
            notificado=False,
            consolidado_dre=consolidado_dre
        ).order_by('ordem')

        comentarios_notificados = ComentarioAnaliseConsolidadoDRE.objects.filter(
            notificado=True,
            consolidado_dre=consolidado_dre
        ).order_by('-notificado_em')

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
            ComentarioAnaliseConsolidadoDRE.reordenar_comentarios(novas_ordens_comentarios=comentarios_de_analise)
        except (ConsolidadoDRE.DoesNotExist, ValidationError):
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
