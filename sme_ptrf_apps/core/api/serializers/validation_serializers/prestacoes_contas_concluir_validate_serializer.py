import logging

from rest_framework import serializers
from sme_ptrf_apps.core.models import Associacao, Periodo

logger = logging.getLogger(__name__)

class PrestacoesContasConcluirValidateSerializer(serializers.Serializer): # noqa
    associacao_uuid = serializers.UUIDField(required=True, allow_null=False)
    periodo_uuid = serializers.UUIDField(required=True, allow_null=False)
    justificativa_acertos_pendentes = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    def validate_associacao_uuid(self, value): # noqa
        try:
            Associacao.by_uuid(value)
        except Associacao.DoesNotExist: # noqa
            logger.error(f'Associação com uuid {value} não encontrada.')
            raise serializers.ValidationError(f"Não foi encontrado um objeto para o uuid de Associação {value}.")

        return value


    def validate_periodo_uuid(self, value): # noqa
        try:
            Periodo.by_uuid(value)
        except Periodo.DoesNotExist: # noqa
            logger.error(f'Período com uuid {value} não encontrado.')
            raise serializers.ValidationError(f"Não foi encontrado um objeto para o uuid de Período {value}.")

        return value
