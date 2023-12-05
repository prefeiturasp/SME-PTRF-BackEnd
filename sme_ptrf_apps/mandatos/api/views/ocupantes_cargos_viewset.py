from rest_framework import mixins, status
from rest_framework.viewsets import GenericViewSet
from waffle.mixins import WaffleFlagMixin

from sme_ptrf_apps.core.api.utils.pagination import CustomPagination
from sme_ptrf_apps.users.permissoes import PermissaoApiUe
from rest_framework.permissions import IsAuthenticated

from sme_ptrf_apps.users.services import SmeIntegracaoService, SmeIntegracaoException
from ...models import OcupanteCargo
from ..serializers import OcupanteCargoSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from requests import ConnectTimeout, ReadTimeout


class OcupantesCargosViewSet(
    WaffleFlagMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet
):
    waffle_flag = "historico-de-membros"
    permission_classes = [IsAuthenticated, PermissaoApiUe]
    lookup_field = 'uuid'
    queryset = OcupanteCargo.objects.all()
    serializer_class = OcupanteCargoSerializer
    pagination_class = CustomPagination

    @action(detail=False, methods=['get'], url_path='codigo-identificacao',
            permission_classes=[IsAuthenticated & PermissaoApiUe])
    def consulta_codigo_identificacao_no_smeintegracao(self, request):
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
                result = SmeIntegracaoService.get_informacao_aluno(codigo_eol)
                return Response(result)
            else:
                result = SmeIntegracaoService.informacao_usuario_sgp(login=rf)
                return Response(result)

        except SmeIntegracaoException as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except ReadTimeout:
            return Response({'detail': 'EOL Timeout'}, status=status.HTTP_400_BAD_REQUEST)
        except ConnectTimeout:
            return Response({'detail': 'EOL Timeout'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='cargos-do-rf',
                permission_classes=[IsAuthenticated & PermissaoApiUe])
    def get_cargos_do_rf_no_smeintegracao(self, request):
        rf = self.request.query_params.get('rf')

        if not rf:
            erro = {
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário enviar o rf'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            cargos = SmeIntegracaoService.get_cargos_do_rf(rf=rf)
            return Response(cargos)

        except SmeIntegracaoException as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except ReadTimeout:
            return Response({'detail': 'EOL Timeout'}, status=status.HTTP_400_BAD_REQUEST)
        except ConnectTimeout:
            return Response({'detail': 'EOL Timeout'}, status=status.HTTP_400_BAD_REQUEST)
