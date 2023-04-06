from rest_framework import serializers
from sme_ptrf_apps.core.models import AnalisePrestacaoConta, AnaliseLancamentoPrestacaoConta, Periodo


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


class GravarConciliacaoAnaliseLancamentoValidateSerializer(serializers.Serializer): # noqa
    uuid_analise_lancamento = serializers.CharField(required=True)
    uuid_periodo = serializers.CharField(required=True)

    def validate_uuid_analise_lancamento(self, value): # noqa
        try:
            AnaliseLancamentoPrestacaoConta.by_uuid(value)
        except AnaliseLancamentoPrestacaoConta.DoesNotExist: # noqa
            raise serializers.ValidationError(f"Não foi encontrado um objeto para o uuid {value}.")

        return value


    def validate_uuid_periodo(self, value): # noqa
        try:
            Periodo.by_uuid(value)
        except Periodo.DoesNotExist: # noqa
            raise serializers.ValidationError(f"Não foi encontrado um objeto para o uuid {value}.")

        return value


class GravarDesconciliacaoAnaliseLancamentoValidateSerializer(serializers.Serializer): # noqa
    uuid_analise_lancamento = serializers.CharField(required=True)

    def validate_uuid_analise_lancamento(self, value): # noqa
        try:
            AnaliseLancamentoPrestacaoConta.by_uuid(value)
        except AnaliseLancamentoPrestacaoConta.DoesNotExist: # noqa
            raise serializers.ValidationError(f"Não foi encontrado um objeto para o uuid {value}.")

        return value
