import logging

from django_filters import rest_framework as filters
from rest_framework import status
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from ..serializers.tecnico_dre_serializer import TecnicoDreSerializer, TecnicoDreCreateSerializer
from ...models import TecnicoDre
from ...services.atribuicao_service import troca_atribuicao_em_lote

logger = logging.getLogger(__name__)

class TecnicosDreViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    lookup_field = 'uuid'
    queryset = TecnicoDre.objects.all()
    serializer_class = TecnicoDreSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('dre__uuid', 'rf')
    def get_serializer_class(self):
        if self.action in ['retrieve', 'list']:
            return TecnicoDreSerializer
        else:
            return TecnicoDreCreateSerializer

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        logger.info('Apagando técnico', obj)
        transferir_para = request.query_params.get('transferir_para')
        if transferir_para:
            try:
                novo_tecnico = TecnicoDre.objects.get(uuid=transferir_para)
                troca_atribuicao_em_lote({'tecnico_atual': f'{obj.uuid}', 'tecnico_novo': f'{novo_tecnico.uuid}'})
            except TecnicoDre.DoesNotExist:
                erro = {
                    'erro': 'Objeto não encontrado.',
                    'mensagem': f"O objeto técnico DRE para o uuid {transferir_para} não foi encontrado na base."
                }
                logger.info('Erro: %r', erro)
                return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        self.perform_destroy(obj)
        return Response(status=status.HTTP_204_NO_CONTENT)
