from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from sme_ptrf_apps.users.permissoes import (PermissaoAPITodosComLeituraOuGravacao,)
from django.core.exceptions import ValidationError
from django.db.models import Q

from ..serializers.analise_valor_reprogramado_prestacao_conta_serializer import \
    AnaliseValorReprogramadoPrestacaoContaSerializer
from ...models import AnaliseValorReprogramadoPrestacaoConta, AnalisePrestacaoConta, ContaAssociacao, AcaoAssociacao


class AnaliseValorReprogramadoPrestacaoContaViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    lookup_field = 'uuid'
    queryset = AnaliseValorReprogramadoPrestacaoConta.objects.all()
    serializer_class = AnaliseValorReprogramadoPrestacaoContaSerializer

    @action(detail=False, methods=['get'], url_path='valores-reprogramados-acao',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def valores_reprogramados_acao(self, request):

        analise_prestacao_conta_uuid = request.query_params.get('analise_prestacao_conta')
        if not analise_prestacao_conta_uuid:
            erro = {
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário enviar o uuid da análise da PC.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            analise_prestacao_conta = AnalisePrestacaoConta.by_uuid(analise_prestacao_conta_uuid)
        except (AnalisePrestacaoConta.DoesNotExist, ValidationError):
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto analise_prestacao_conta para o uuid {analise_prestacao_conta_uuid} não foi encontrado na base."
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        conta_associacao_uuid = self.request.query_params.get('conta_associacao')
        if not conta_associacao_uuid:
            erro = {
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário enviar o uuid da conta da associação.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            conta_associacao = ContaAssociacao.objects.get(uuid=conta_associacao_uuid)
        except (ContaAssociacao.DoesNotExist, ValidationError):
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto conta-associação para o uuid {conta_associacao_uuid} não foi encontrado na base."
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        acao_associacao_uuid = request.query_params.get('acao_associacao')
        if not acao_associacao_uuid:
            erro = {
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário enviar o uuid da ação da associação.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            acao_associacao = AcaoAssociacao.objects.get(uuid=acao_associacao_uuid)
        except (AcaoAssociacao.DoesNotExist, ValidationError):
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto ação-associação para o uuid {acao_associacao_uuid} não foi encontrado."
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        qs = AnaliseValorReprogramadoPrestacaoConta.objects.all()

        qs = qs.filter(Q(analise_prestacao_conta__uuid=analise_prestacao_conta_uuid) & Q(conta_associacao__uuid=conta_associacao_uuid) & Q(acao_associacao__uuid=acao_associacao_uuid))

        result = AnaliseValorReprogramadoPrestacaoContaSerializer(qs, many=True).data

        return Response(result, status=status.HTTP_200_OK)
