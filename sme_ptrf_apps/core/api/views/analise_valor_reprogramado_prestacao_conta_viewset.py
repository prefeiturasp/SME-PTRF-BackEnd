from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from sme_ptrf_apps.users.permissoes import (PermissaoAPITodosComLeituraOuGravacao, )
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

        qs = qs.filter(Q(analise_prestacao_conta__uuid=analise_prestacao_conta_uuid) & Q(
            conta_associacao__uuid=conta_associacao_uuid) & Q(acao_associacao__uuid=acao_associacao_uuid))

        result = AnaliseValorReprogramadoPrestacaoContaSerializer(qs, many=True).data

        return Response(result, status=status.HTTP_200_OK)

    @action(detail=False, url_path='salvar-valores-reprogramados-acao', methods=['post'],
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def salvar_valores_reprogramados_acao(self, request):

        dados_analise_valor_reprogramado = self.request.data

        if not dados_analise_valor_reprogramado:
            erro = {
                'erro': 'Dados da Análise Vazio',
                'mensagem': 'Os dados da análise não foram enviados'
            }

            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        # A verificação não foi feita com if not dados_analise_valor_reprogramado.get('DADO_A_VERIFICAR'), pois o campo valor_saldo_reprogramado_correto pode ser False
        try:
            analise_prestacao_conta_uuid = dados_analise_valor_reprogramado['analise_prestacao_conta']
            conta_associacao_uuid = dados_analise_valor_reprogramado['conta_associacao']
            acao_associacao_uuid = dados_analise_valor_reprogramado['acao_associacao']
            valor_saldo_reprogramado_correto = dados_analise_valor_reprogramado['valor_saldo_reprogramado_correto']
            novo_saldo_reprogramado_custeio = dados_analise_valor_reprogramado['novo_saldo_reprogramado_custeio']
            novo_saldo_reprogramado_capital = dados_analise_valor_reprogramado['novo_saldo_reprogramado_capital']
            novo_saldo_reprogramado_livre = dados_analise_valor_reprogramado['novo_saldo_reprogramado_livre']
        except:
            erro = {
                'erro': 'Dados incompletos',
                'mensagem': 'Não foram enviados todos os dados necessários'
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

        try:
            conta_associacao = ContaAssociacao.objects.get(uuid=conta_associacao_uuid)
        except (ContaAssociacao.DoesNotExist, ValidationError):
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto conta-associação para o uuid {conta_associacao_uuid} não foi encontrado na base."
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

        if valor_saldo_reprogramado_correto:
            novo_saldo_reprogramado_custeio = None
            novo_saldo_reprogramado_capital = None
            novo_saldo_reprogramado_livre = None

        try:
            AnaliseValorReprogramadoPrestacaoConta.objects.create(
                analise_prestacao_conta=analise_prestacao_conta,
                conta_associacao=conta_associacao,
                acao_associacao=acao_associacao,
                valor_saldo_reprogramado_correto=valor_saldo_reprogramado_correto,
                novo_saldo_reprogramado_custeio=novo_saldo_reprogramado_custeio,
                novo_saldo_reprogramado_capital=novo_saldo_reprogramado_capital,
                novo_saldo_reprogramado_livre=novo_saldo_reprogramado_livre
            )
        except Exception as err:
            erro = {
                'erro': 'Erro ao salvar Analise de Valores Reprogramados',
                'mensagem': f'Não foi possível salvar a analise de valores reprogramados | {err}'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        resultado = {
            'mensagem': 'Analise de valores reprogramados salva com sucesso'
        }

        return Response(resultado, status=status.HTTP_200_OK)
