import logging

from rest_framework import serializers

from sme_ptrf_apps.core.models import Associacao

logger = logging.getLogger(__name__)

class MandatoVigenteValidateSerializer(serializers.Serializer): # noqa
    associacao_uuid = serializers.CharField(required=True)

    def validate_associacao_uuid(self, value):

        try:
            Associacao.by_uuid(value)
        except Associacao.DoesNotExist: # noqa
            raise serializers.ValidationError(f"Não foi encontrado um objeto para o uuid {value}.")

        return value
