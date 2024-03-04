from datetime import date
import logging
from rest_framework import serializers
from sme_ptrf_apps.core.models.associacao import Associacao
from sme_ptrf_apps.mandatos.models import Composicao

logger = logging.getLogger(__name__)

class CargosComposicaoValidateSerializer(serializers.Serializer): # noqa
    composicao_uuid = serializers.CharField(required=True)

    def validate_composicao_uuid(self, value):
        try:
            Composicao.by_uuid(value)
        except Composicao.DoesNotExist: # noqa
            raise serializers.ValidationError(f"Não foi encontrado um objeto para o uuid {value}.")

        return value

class CargosComposicaoPorDataValidateSerializer(serializers.Serializer):
    associacao_uuid = serializers.CharField(required=True)
    data = serializers.DateField(required=True)

    def validate_associacao_uuid(self, value):
        try:
            Associacao.objects.get(uuid=value)
        except Associacao.DoesNotExist:
            raise serializers.ValidationError(f"Não foi encontrado um objeto para o uuid {value}.")
        
    def validate_data(self, value):
        if not isinstance(value, date):
            raise serializers.ValidationError(f"O valor fornecido não é uma data válida.")
        return value
        