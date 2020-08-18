from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from ..serializers import UnidadeSerializer
from ...models import Unidade
from ...services import monta_unidade_para_atribuicao


class UnidadesViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    lookup_field = 'uuid'
    queryset = Unidade.objects.all()
    serializer_class = UnidadeSerializer

    @action(detail=False, url_path='para-atribuicao')
    def para_atribuicao(self, request, *args, **kwargs):
        dre_uuid = request.query_params.get('dre_uuid')
        periodo = request.query_params.get('periodo')

        if not dre_uuid or not periodo:
            erro = {
                'erro': 'parametros_requerido',
                'mensagem': 'É necessário enviar o uuid da dre (dre_uuid) e o periodo como parâmetros.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        list_unidades = monta_unidade_para_atribuicao(dre_uuid, periodo)
        return Response(list_unidades)
