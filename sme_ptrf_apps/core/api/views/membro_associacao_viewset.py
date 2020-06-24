from requests import ConnectTimeout, ReadTimeout

from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework import status

from sme_ptrf_apps.core.api.serializers import MembroAssociacaoCreateSerializer, MembroAssociacaoListSerializer
from sme_ptrf_apps.core.models import MembroAssociacao
from sme_ptrf_apps.core.services import TerceirizadasException, TerceirizadasService


class MembroAssociacaoViewSet(mixins.RetrieveModelMixin,
                              mixins.ListModelMixin,
                              mixins.CreateModelMixin,
                              mixins.UpdateModelMixin,
                              mixins.DestroyModelMixin,
                              GenericViewSet):

    lookup_field = 'uuid'
    permission_classes = [AllowAny]
    serializer_class = MembroAssociacaoListSerializer
    queryset = MembroAssociacao.objects.all()

    def get_serializer_class(self):
        if self.action in ['retrieve', 'list']:
            return MembroAssociacaoListSerializer
        else:
            return MembroAssociacaoCreateSerializer

    @action(detail=False, methods=['get'], url_path='codigo-identificacao')
    def consulta_codigo_identificacao(self, request):
        rf = self.request.query_params.get('rf')
        codigo_eol = self.request.query_params.get('codigo-eol')

        if not rf and not codigo_eol:
            erro = {
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário enviar o rf ou código eol.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            if codigo_eol:
                result = TerceirizadasService.get_informacao_aluno(codigo_eol)
                return Response(result)
            else:
                result = TerceirizadasService.get_informacao_servidor(rf)
                return Response(result)
        except TerceirizadasException as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except ReadTimeout:
            return Response({'detail': 'EOL Timeout'}, status=status.HTTP_400_BAD_REQUEST)
        except ConnectTimeout:
            return Response({'detail': 'EOL Timeout'}, status=status.HTTP_400_BAD_REQUEST)
