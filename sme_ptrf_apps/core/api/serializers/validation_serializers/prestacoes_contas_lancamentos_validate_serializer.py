import logging

from rest_framework import serializers
from sme_ptrf_apps.core.models import AnalisePrestacaoConta, ContaAssociacao, AcaoAssociacao
from sme_ptrf_apps.despesas.models import TipoDocumento, TipoTransacao

logger = logging.getLogger(__name__)

class PrestacoesContasLancamentosValidateSerializer(serializers.Serializer): # noqa
    analise_prestacao = serializers.UUIDField(required=True, allow_null=False)
    conta_associacao = serializers.UUIDField(required=True, allow_null=False)
    acao_associacao = serializers.UUIDField(required=False, allow_null=True)
    tipo = serializers.CharField(required=False, allow_null=True)
    ordenar_por_imposto = serializers.BooleanField(required=False, allow_null=True)
    filtrar_por_numero_de_documento = serializers.CharField(required=False, allow_null=True)
    filtrar_por_data_inicio = serializers.DateField(required=False, allow_null=True)
    filtrar_por_data_fim = serializers.DateField(required=False, allow_null=True)
    filtrar_por_tipo_de_documento = serializers.IntegerField(required=False, allow_null=True)
    filtrar_por_tipo_de_pagamento = serializers.IntegerField(required=False, allow_null=True)
    filtrar_por_nome_fornecedor = serializers.CharField(required=False, allow_null=True)

    def validate_analise_prestacao(self, value): # noqa
        try:
            analise = AnalisePrestacaoConta.by_uuid(value)
        except AnalisePrestacaoConta.DoesNotExist: # noqa
            logger.error(f'AnalisePrestacaoConta com uuid {value} não encontrada.')
            raise serializers.ValidationError(f"Não foi encontrado um objeto para o uuid de AnalisePrestacaoConta {value}.")

        prestacao_conta = self.context.get("prestacao_conta")
        if analise.prestacao_conta != prestacao_conta:
            logger.error(f'AnalisePrestacaoConta com uuid {value} não pertence a prestação de conta {prestacao_conta.uuid}.')
            raise serializers.ValidationError(f"O uuid de AnalisePrestacaoConta {value} não pertence a esta Prestação de Contas.")

        return value


    def validate_conta_associacao(self, value): # noqa
        try:
            conta_associacao = ContaAssociacao.by_uuid(value)
        except ContaAssociacao.DoesNotExist: # noqa
            logger.error(f'ContaAssociacao com uuid {value} não encontrada.')
            raise serializers.ValidationError(f"Não foi encontrado um objeto para o uuid de ContaAssociacao {value}.")

        prestacao_conta = self.context.get("prestacao_conta")
        if conta_associacao.associacao != prestacao_conta.associacao:
            logger.error(f'ContaAssociacao com uuid {value} não pertence a associação da prestação de conta {prestacao_conta.uuid}.')
            raise serializers.ValidationError(f"O uuid de ContaAssociacao {value} não pertence a associacao dessa Prestação de Contas.")

        return value

    def validate_acao_associacao(self, value):  # noqa
        if value:
            try:
                acao_associacao = AcaoAssociacao.by_uuid(value)
            except AcaoAssociacao.DoesNotExist:
                logger.error(f'AcaoAssociacao com uuid {value} não encontrada.')
                raise serializers.ValidationError(
                    f"Não foi encontrado um objeto para o uuid de AcaoAssociacao {value}.")
            prestacao_conta = self.context.get("prestacao_conta")
            if acao_associacao.associacao != prestacao_conta.associacao:
                logger.error(
                    f'AcaoAssociacao com uuid {value} não pertence a associação da prestação de conta {prestacao_conta.uuid}.')
                raise serializers.ValidationError(
                    f"O uuid de AcaoAssociacao {value} não pertence a associacao dessa Prestação de Contas.")

        return value


    def validate_tipo(self, value): # noqa
        if value and value not in ['CREDITOS', 'GASTOS']:
            logger.error(f'Tipo {value} não é válido.')
            raise serializers.ValidationError(f"O tipo {value} não é válido. Esperado: CREDITOS ou GASTOS.")
        return value

    def validate_filtrar_por_tipo_de_documento(self, value):
        if value:
            try:
                TipoDocumento.by_id(value)
            except TipoDocumento.DoesNotExist:
                logger.error(f'TipoDocumento com id {value} não encontrado.')
                raise serializers.ValidationError(f"Não foi encontrado um objeto para o id de TipoDocumento {value}.")
        return value

    def validate_filtrar_por_tipo_de_pagamento(self, value):
        if value:
            try:
                TipoTransacao.by_id(value)
            except TipoTransacao.DoesNotExist:
                logger.error(f'TipoTransacao com id {value} não encontrado.')
                raise serializers.ValidationError(f"Não foi encontrado um objeto para o id de TipoTrabsacao {value}.")
        return value
