from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from sme_ptrf_apps.users.permissoes import (PermissaoAPITodosComLeituraOuGravacao, )
from django.core.exceptions import ValidationError
from django.db.models import Q


from ...models import AnalisePrestacaoConta, ContaAssociacao, AcaoAssociacao

from ...models import AnaliseContaPrestacaoConta, PrestacaoConta
from ..serializers.analise_conta_prestacao_conta_serializer import AnaliseContaPrestacaoContaRetrieveSerializer


class AnaliseContaPrestacaoContaViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    lookup_field = 'uuid'
    queryset = AnaliseContaPrestacaoConta.objects.all()
    serializer_class = AnaliseContaPrestacaoContaRetrieveSerializer

    @action(detail=False, methods=['get'], url_path='get-ajustes-saldo-conta',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def get_ajustes_saldo_conta(self, request):

        analise_prestacao_conta_uuid = request.query_params.get('analise_prestacao_conta')
        prestacao_conta_uuid = request.query_params.get('prestacao_conta')

        if not prestacao_conta_uuid:
            erro = {
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário enviar o uuid da PC.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            prestacao_conta = PrestacaoConta.by_uuid(prestacao_conta_uuid)
        except (PrestacaoConta.DoesNotExist, ValidationError):
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto prestacao_conta para o uuid {prestacao_conta_uuid} não foi encontrado na base."
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

        qs = AnaliseContaPrestacaoConta.objects.all()
        qs = qs.filter(Q(conta_associacao__uuid=conta_associacao_uuid) & Q(
            prestacao_conta__uuid=prestacao_conta_uuid) & Q(analise_prestacao_conta__uuid=analise_prestacao_conta_uuid))

        result = AnaliseContaPrestacaoContaRetrieveSerializer(qs, many=True).data

        return Response(result, status=status.HTTP_200_OK)

    @action(detail=False, url_path='salvar-ajustes-saldo-conta', methods=['post'],
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def salvar_ajustes_saldo_conta(self, request):
        dados_analise_saldo = self.request.data

        if not dados_analise_saldo:
            erro = {
                'erro': 'Dados da Análise Vazio',
                'mensagem': 'Os dados da análise não foram enviados'
            }

            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        analise_prestacao_conta_uuid = dados_analise_saldo['analise_prestacao_conta']
        conta_associacao_uuid = dados_analise_saldo['conta_associacao']
        prestacao_conta_uuid = dados_analise_saldo['prestacao_conta']
        data_extrato = dados_analise_saldo['data_extrato']
        saldo_extrato = dados_analise_saldo['saldo_extrato']
        solicitar_envio_do_comprovante_do_saldo_da_conta = dados_analise_saldo.get('solicitar_envio_do_comprovante_do_saldo_da_conta', False)
        observacao_solicitar_envio_do_comprovante_do_saldo_da_conta = dados_analise_saldo.get('observacao_solicitar_envio_do_comprovante_do_saldo_da_conta', None)

        try:
            analise_prestacao_conta = AnalisePrestacaoConta.by_uuid(analise_prestacao_conta_uuid)
        except (AnalisePrestacaoConta.DoesNotExist, ValidationError):
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto analise_prestacao_conta para o uuid {analise_prestacao_conta_uuid} não foi encontrado na base."
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            prestacao_conta = PrestacaoConta.by_uuid(prestacao_conta_uuid)
        except (PrestacaoConta.DoesNotExist, ValidationError):
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto prestacao_conta para o uuid {prestacao_conta_uuid} não foi encontrado na base."
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

        try:
            AnaliseContaPrestacaoConta.objects.create(
                analise_prestacao_conta=analise_prestacao_conta,
                conta_associacao=conta_associacao,
                prestacao_conta=prestacao_conta,
                data_extrato=data_extrato,
                saldo_extrato=saldo_extrato,
                solicitar_envio_do_comprovante_do_saldo_da_conta=solicitar_envio_do_comprovante_do_saldo_da_conta,
                observacao_solicitar_envio_do_comprovante_do_saldo_da_conta=observacao_solicitar_envio_do_comprovante_do_saldo_da_conta,
            )
        except Exception as err:
            erro = {
                'erro': 'Erro ao salvar Analise de Ajustes de saldo',
                'mensagem': f'Não foi possível salvar a analise de ajustes de saldo | {err}'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        resultado = {
            'mensagem': 'Analise de ajustes de saldo por conta salva com sucesso'
        }

        return Response(resultado, status=status.HTTP_200_OK)
