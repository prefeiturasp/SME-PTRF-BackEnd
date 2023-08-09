import logging
from rest_framework import serializers
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
