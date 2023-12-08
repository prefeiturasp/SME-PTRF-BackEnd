from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework import status
from sme_ptrf_apps.core.api.serializers import ProcessoAssociacaoCreateSerializer, ProcessoAssociacaoRetrieveSerializer
from sme_ptrf_apps.core.models import ProcessoAssociacao
from sme_ptrf_apps.users.permissoes import PermissaoApiDre


class ProcessosAssociacaoViewSet(mixins.RetrieveModelMixin,
                                 mixins.CreateModelMixin,
                                 mixins.UpdateModelMixin,
                                 mixins.DestroyModelMixin,
                                 GenericViewSet):
    lookup_field = 'uuid'
    permission_classes = [IsAuthenticated & PermissaoApiDre]
    serializer_class = ProcessoAssociacaoRetrieveSerializer
    queryset = ProcessoAssociacao.objects.all()

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProcessoAssociacaoRetrieveSerializer
        else:
            return ProcessoAssociacaoCreateSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        if instance.e_o_ultimo_processo_do_ano_com_pcs_vinculada:
            msg = {
                'erro': 'possui_prestacao_de_conta_vinculada',
                'mensagem': 'Não é possível excluir o número desse processo SEI, pois este já está vinculado a uma prestação de contas. Caso necessário, é possível editá-lo.'
            }
            return Response(msg, status=status.HTTP_400_BAD_REQUEST)

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
