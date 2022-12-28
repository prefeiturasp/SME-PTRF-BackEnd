from rest_framework import serializers
from sme_ptrf_apps.dre.models import AnaliseConsolidadoDre

class AnaliseConsolidadoDreSerializer(serializers.Serializer): # noqa
    analise_consolidado_uuid = serializers.CharField(required=True)

    def validate_analise_consolidado_uuid(self, value): # noqa
        try:
            AnaliseConsolidadoDre.by_uuid(value)
        except AnaliseConsolidadoDre.DoesNotExist: # noqa
            raise serializers.ValidationError(f"Não foi encontrado um objeto para o uuid {value}.")

        return value
