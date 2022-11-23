from rest_framework import serializers
from sme_ptrf_apps.core.models import AnalisePrestacaoConta


class TabelasValidateSerializer(serializers.Serializer): # noqa
    uuid_analise_prestacao = serializers.CharField(required=True)
    visao = serializers.CharField(required=True)

    def validate_uuid_analise_prestacao(self, value): # noqa
        try:
            AnalisePrestacaoConta.by_uuid(value)
        except AnalisePrestacaoConta.DoesNotExist: # noqa
            raise serializers.ValidationError(f"Não foi encontrado um objeto para o uuid {value}.")

        return value


    def validate_visao(self, value): # noqa
        if value != "UE" and value != "DRE":
            raise serializers.ValidationError(f"Apenas visão UE e DRE são aceitaveis")

        return value
