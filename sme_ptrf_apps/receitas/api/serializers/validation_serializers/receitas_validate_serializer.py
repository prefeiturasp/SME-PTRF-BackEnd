import logging

from rest_framework import serializers
from sme_ptrf_apps.core.models.associacao import Associacao

logger = logging.getLogger(__name__)


class ValidarPeriodosAssociacaoEncerradaValidationSerializer(serializers.Serializer):
    associacao_uuid = serializers.UUIDField(required=True)

    def validate_associacao_uuid(self, value): # noqa
        try:
            Associacao.by_uuid(value)
        except Associacao.DoesNotExist: # noqa
            logger.error(f'Associacao com uuid {value} não encontrada.')
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto Associação para o uuid {value} não foi encontrado na base."
            }
            raise serializers.ValidationError(erro)

        return value


class ValidarDataDaReceitaAssociacaoEncerradaValidationSerializer(serializers.Serializer):
    associacao_uuid = serializers.UUIDField(required=True)
    data_da_receita = serializers.DateField(required=True)

    def validate_associacao_uuid(self, value): # noqa
        try:
            Associacao.by_uuid(value)
        except Associacao.DoesNotExist: # noqa
            logger.error(f'Associacao com uuid {value} não encontrada.')
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto Associação para o uuid {value} não foi encontrado na base."
            }
            raise serializers.ValidationError(erro)

        return value
