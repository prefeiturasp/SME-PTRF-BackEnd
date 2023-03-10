from rest_framework import serializers
from django.core.exceptions import ValidationError

from sme_ptrf_apps.core.models import Associacao, Periodo


class FalhaGeracaoPcValidationSerializer(serializers.Serializer): # noqa
    associacao = serializers.CharField(required=True)

    def validate_associacao(self, value): # noqa
        try:
            Associacao.by_uuid(value)
        except (Associacao.DoesNotExist, ValidationError): # noqa
            raise serializers.ValidationError(f"Não foi encontrado um objeto Associacao para o uuid {value}.")

        return value

