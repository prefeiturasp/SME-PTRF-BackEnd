from rest_framework import mixins, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response

from ..serializers.solicitacao_encerramento_conta_associacao_serializer import SolicitacaoEncerramentoContaAssociacaoSerializer
from ...models import SolicitacaoEncerramentoContaAssociacao

class SolicitacaoEncerramentoContaAssociacaoViewset(mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        mixins.CreateModelMixin,
                        mixins.UpdateModelMixin,
                        mixins.DestroyModelMixin,
                        GenericViewSet):
    permission_classes = [IsAuthenticated]
    lookup_field = 'uuid'
    queryset = SolicitacaoEncerramentoContaAssociacao.objects.all()
    serializer_class = SolicitacaoEncerramentoContaAssociacaoSerializer

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()

        if obj.pode_apagar:
            self.perform_destroy(obj)
        else:
            return Response({'mensagem': 'Essa solicitação não pode ser apagada.'}, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_204_NO_CONTENT)
