from django.db.utils import IntegrityError
from rest_framework import mixins
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from ..serializers.prestacao_conta_serializer import PrestacaoContaLookUpSerializer
from ...models import PrestacaoConta
from ...services import iniciar_prestacao_de_contas


class PrestacoesContasViewSet(mixins.RetrieveModelMixin,
                              mixins.UpdateModelMixin,
                              GenericViewSet):
    permission_classes = [AllowAny]
    lookup_field = 'uuid'
    queryset = PrestacaoConta.objects.all()
    serializer_class = PrestacaoContaLookUpSerializer

    @action(detail=False, url_path='por-conta-e-periodo')
    def por_conta_e_periodo(self, request):
        conta_associacao_uuid = request.query_params.get('conta_associacao_uuid')
        periodo_uuid = request.query_params.get('periodo_uuid')
        return Response(PrestacaoContaLookUpSerializer(
            self.queryset.filter(conta_associacao__uuid=conta_associacao_uuid).filter(
                periodo__uuid=periodo_uuid).first(), many=False).data)

    @action(detail=False, methods=['post'])
    def iniciar(self, request):
        conta_associacao_uuid = request.query_params.get('conta_associacao_uuid')
        periodo_uuid = request.query_params.get('periodo_uuid')

        if not conta_associacao_uuid or not periodo_uuid:
            erro = {
                'erro': 'parametros_requerido',
                'mensagem': 'É necessário enviar o uuid do período e o uuid da conta da associação.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            nova_prestacao_de_contas = iniciar_prestacao_de_contas(conta_associacao_uuid, periodo_uuid)
        except(IntegrityError):
            erro = {
                'erro': 'prestacao_ja_iniciada',
                'mensagem': 'Você não pode iniciar uma prestação de contas que já foi iniciada.'
            }
            return Response(erro, status=status.HTTP_409_CONFLICT)
        else:
            return Response(PrestacaoContaLookUpSerializer(nova_prestacao_de_contas, many=False).data,
                            status=status.HTTP_201_CREATED)
